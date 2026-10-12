const pptxgen = require("pptxgenjs");
const pres = new pptxgen(); pres.layout = "LAYOUT_16x9";
const title = (s, t) => s.addText(t, { x: 0.5, y: 0.3, w: 9, h: 0.8, fontSize: 30, bold: true, color: "1F3864", isTextBox: true });
const bullets = (s, items) => s.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
  { x: 0.7, y: 1.4, w: 8.5, h: 3, fontSize: 22, paraSpaceAfter: 10, valign: "top", isTextBox: true });
let s = pres.addSlide();
s.addText("Nimbus Product Launch", { x: 0.5, y: 1.8, w: 9, h: 1, fontSize: 40, bold: true, align: "center", color: "1F3864", isTextBox: true });
s.addText("Prepared by Team Kestrel", { x: 0.5, y: 2.9, w: 9, h: 0.6, fontSize: 20, align: "center", color: "555555", isTextBox: true });
s = pres.addSlide(); title(s, "Key Targets");
bullets(s, ["Q3 Target: 1,250 units", "Launch city: Hyderabad", "Budget: ₹7.5 lakh"]);
s = pres.addSlide(); title(s, "Team");
bullets(s, ["Lead: Arjun Mehta", "Design: Priya Nair", "Sales: Farhan Qureshi"]);
s = pres.addSlide(); title(s, "Pricing");
const hd = { bold: true, fill: { color: "D9E2F3" } };
s.addTable([
  [{ text: "Plan", options: hd }, { text: "Price", options: hd }, { text: "Users", options: hd }],
  ["Basic", "₹499", "5"], ["Pro", "₹1,299", "25"], ["Enterprise", "₹4,999", "200"],
], { x: 1, y: 1.5, w: 8, colW: [3, 2.5, 2.5], fontSize: 18, border: { type: "solid", pt: 1, color: "000000" } });
pres.writeFile({ fileName: "data/04_slides.pptx" }).then(() => console.log("pptx done"));
