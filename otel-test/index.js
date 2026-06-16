const { trace, context, SpanStatusCode } = require("@opentelemetry/api");
const {
  BasicTracerProvider,
  ConsoleSpanExporter,
  SimpleSpanProcessor,
} = require("@opentelemetry/sdk-trace-base");
const {
  AsyncLocalStorageContextManager,
} = require("@opentelemetry/context-async-hooks");
const { resourceFromAttributes } = require("@opentelemetry/resources");
const {
  ATTR_SERVICE_NAME,
  ATTR_SERVICE_VERSION,
} = require("@opentelemetry/semantic-conventions");

// ---------------------------------------------------------------------------
// 1. Set up the SDK
// ---------------------------------------------------------------------------
// A "resource" describes WHO is producing the telemetry (the service name and
// version show up on every span). The ConsoleSpanExporter just prints finished
// spans to the terminal so we can see them without any backend.
const provider = new BasicTracerProvider({
  resource: resourceFromAttributes({
    [ATTR_SERVICE_NAME]: "order-service",
    [ATTR_SERVICE_VERSION]: "0.1.0",
  }),
  spanProcessors: [new SimpleSpanProcessor(new ConsoleSpanExporter())],
});
trace.setGlobalTracerProvider(provider);

// The context manager is what lets a span stay "active" across `await`s, so
// child spans can find their parent automatically. Without it, every span would
// become its own separate trace instead of nesting into a tree.
context.setGlobalContextManager(new AsyncLocalStorageContextManager());

// A tracer is what you use to create spans throughout your code.
const tracer = trace.getTracer("order-example");

// Small helper to simulate work that takes some time.
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// ---------------------------------------------------------------------------
// 2. Create spans for the work you want to measure
// ---------------------------------------------------------------------------
// `startActiveSpan` makes the span "active" for everything that runs inside the
// callback. Any span created in there automatically becomes its CHILD, which is
// how OpenTelemetry builds a trace tree without you passing anything around.

async function chargePayment(orderId, amount) {
  return tracer.startActiveSpan("charge-payment", async (span) => {
    // Attributes are key/value metadata that describe this span.
    span.setAttribute("order.id", orderId);
    span.setAttribute("payment.amount", amount);

    await sleep(150); // pretend we call a payment provider

    // Events are timestamped log points within a span.
    span.addEvent("payment-authorized");
    span.end(); // ALWAYS end a span, or it never gets exported.
  });
}

async function reserveStock(orderId, items) {
  return tracer.startActiveSpan("reserve-stock", async (span) => {
    span.setAttribute("order.id", orderId);
    span.setAttribute("items.count", items);

    await sleep(100);

    if (items > 5) {
      // Record failures: attach the error and set an ERROR status so the span
      // shows up clearly when you search for problems.
      const error = new Error("Not enough stock available");
      span.recordException(error);
      span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
      span.end();
      throw error;
    }

    span.setStatus({ code: SpanStatusCode.OK });
    span.end();
  });
}

// The top-level span. Its children (charge-payment, reserve-stock) all roll up
// into this one trace, so you can see the whole operation as a tree.
async function processOrder(order) {
  return tracer.startActiveSpan("process-order", async (span) => {
    span.setAttribute("order.id", order.id);
    try {
      await chargePayment(order.id, order.amount);
      await reserveStock(order.id, order.items);
      span.setStatus({ code: SpanStatusCode.OK });
      console.log(`\n✅ Order ${order.id} processed\n`);
    } catch (err) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
      console.log(`\n❌ Order ${order.id} failed: ${err.message}\n`);
    } finally {
      span.end();
    }
  });
}

// ---------------------------------------------------------------------------
// 3. Run it
// ---------------------------------------------------------------------------
async function main() {
  // A successful order...
  await processOrder({ id: "A-1001", amount: 49.99, items: 2 });
  // ...and one that fails on stock to show error reporting.
  await processOrder({ id: "A-1002", amount: 19.99, items: 9 });

  // Flush any pending spans before the process exits.
  await provider.forceFlush();
  await provider.shutdown();
}

main();
