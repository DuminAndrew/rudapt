import express from "express";
import puppeteer from "puppeteer";

const PORT = parseInt(process.env.PORT || "9000", 10);
const TOKEN = process.env.PDF_SERVICE_TOKEN || "";

const app = express();
app.use(express.json({ limit: "5mb" }));

let browserPromise = null;
async function getBrowser() {
  if (!browserPromise) {
    browserPromise = puppeteer.launch({
      headless: "new",
      args: [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--font-render-hinting=none",
      ],
    });
  }
  return browserPromise;
}

app.get("/health", (_req, res) => res.json({ status: "ok" }));

app.post("/render", async (req, res) => {
  if (TOKEN && req.headers["x-pdf-token"] !== TOKEN) {
    return res.status(401).send("unauthorized");
  }
  const { html, format = "A4", margin } = req.body || {};
  if (!html) return res.status(400).send("html required");

  let page;
  try {
    const browser = await getBrowser();
    page = await browser.newPage();
    await page.setContent(html, { waitUntil: "networkidle0", timeout: 30000 });
    const pdf = await page.pdf({
      format,
      printBackground: true,
      margin: margin || { top: "20mm", right: "16mm", bottom: "20mm", left: "16mm" },
    });
    res.setHeader("Content-Type", "application/pdf");
    res.send(pdf);
  } catch (e) {
    console.error("render error:", e);
    res.status(500).send(String(e?.message || e));
  } finally {
    if (page) await page.close().catch(() => {});
  }
});

app.listen(PORT, () => console.log(`pdf-service listening on :${PORT}`));
