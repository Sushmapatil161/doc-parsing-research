const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, AlignmentType, LevelFormat, Header, Footer, PageNumber, ColumnBreak, PageBreak,
  BorderStyle, ShadingType } = require("docx");

const numbering = { config: [
  { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
]};
const styles = { default: { document: { run: { font: "Arial", size: 22 } } } };
const p = (t) => new Paragraph({ children: [new TextRun(t)], spacing: { after: 120 } });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const bullet = (t) => new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun(t)] });
const num = (t) => new Paragraph({ numbering: { reference: "numbers", level: 0 }, children: [new TextRun(t)] });
const A4 = { size: { width: 11906, height: 16838 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } };
const save = async (doc, name) => fs.writeFileSync("data/" + name, await Packer.toBuffer(doc));

(async () => {
// 01 basic
await save(new Document({ styles, numbering, sections: [{ properties: { page: A4 }, children: [
  h1("Project Falcon Overview"),
  p("Project Falcon is an internal initiative with project code QX-7741."),
  h2("Goals"),
  bullet("Reduce processing time by 35 percent"),
  bullet("Launch the Orbit dashboard"),
  bullet("Train 120 staff members"),
  h2("Timeline"),
  num("Planning starts in March 2026"),
  num("Pilot runs in Pune office"),
  num("Full rollout by December 2026"),
]}]}), "01_basic.docx");

// 02 table with merged header cell
const border = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const borders = { top: border, bottom: border, left: border, right: border };
const W = [2626, 2200, 2100, 2100]; // sums to 9026
const cell = (t, i, opts = {}) => new TableCell({ borders, width: { size: opts.span ? W[i] + W[i+1] : W[i], type: WidthType.DXA },
  columnSpan: opts.span ? 2 : undefined, rowSpan: opts.rowSpan,
  shading: opts.head ? { fill: "D9E2F3", type: ShadingType.CLEAR } : undefined,
  margins: { top: 80, bottom: 80, left: 120, right: 120 },
  children: [new Paragraph({ alignment: opts.span ? AlignmentType.CENTER : AlignmentType.LEFT,
    children: [new TextRun({ text: t, bold: !!opts.head })] })] });
const table = new Table({ width: { size: 9026, type: WidthType.DXA }, columnWidths: W, rows: [
  new TableRow({ children: [cell("Region", 0, { head: true, rowSpan: 2 }), cell("Sales (₹)", 1, { head: true, rowSpan: 2 }), cell("Q3 2026", 2, { head: true, span: true })] }),
  new TableRow({ children: [cell("July", 2, { head: true }), cell("August", 3, { head: true })] }),
  new TableRow({ children: [cell("Bengaluru Office", 0), cell("48,213", 1), cell("15,400", 2), cell("16,050", 3)] }),
  new TableRow({ children: [cell("Mumbai Office", 0), cell("39,870", 1), cell("12,900", 2), cell("13,300", 3)] }),
  new TableRow({ children: [cell("Delhi Office", 0), cell("27,645", 1), cell("9,100", 2), cell("9,200", 3)] }),
]});
await save(new Document({ styles, sections: [{ properties: { page: A4 }, children: [
  h1("Zentrix Corp Quarterly Sales"),
  p("The table below shows regional sales. The Q3 2026 header spans two month columns, and Region and Sales span two header rows."),
  table,
  p(""),
  p("Prepared by the Zentrix finance team."),
]}]}), "02_table.docx");

// 03 two-column
const left = [
  "Orion Labs was founded in 2019 in Mysuru.",
  "The lab studies solar battery storage and employs 42 researchers.",
  "Its main product is the Helios cell, which stores energy for small farms.",
  "Orion Labs plans to open a second lab in Hubballi next year.",
];
const right = [
  "Delta 9 is a logistics startup based in Chennai.",
  "It operates 18 delivery vans and serves 3,400 customers.",
  "Its founder is Meera Rao, a former railway engineer.",
  "Delta 9 delivers mainly groceries and medicines across the city.",
];
await save(new Document({ styles, sections: [
  { properties: { page: A4 }, children: [h1("Regional Company Profiles"), p("Two unrelated companies are described side by side below.")] },
  { properties: { page: A4, type: "continuous", column: { count: 2, space: 708 } }, children: [
    h2("Orion Labs"), ...left.map(p),
    new Paragraph({ children: [new ColumnBreak()] }),
    h2("Delta 9"), ...right.map(p),
  ]},
]}), "03_two_column.docx");

// 06 header/footer/page numbers
await save(new Document({ styles, sections: [{ properties: { page: A4 },
  headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun("Confidential – Nimbus Ltd")] })] }) },
  footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
    children: [new TextRun("Internal Report 2026 – Page "), new TextRun({ children: [PageNumber.CURRENT] }), new TextRun(" of "), new TextRun({ children: [PageNumber.TOTAL_PAGES] })] })] }) },
  children: [
    h1("Nimbus Ltd Cost Audit"),
    p("This report summarises the internal cost audit carried out in 2026."),
    p("The audit was led by Rohan Das."),
    new Paragraph({ children: [new PageBreak()] }),
    h2("Findings"),
    p("Most savings came from renegotiated vendor contracts and lower travel costs."),
    p("Total savings reached ₹2,15,000."),
    new Paragraph({ children: [new PageBreak()] }),
    h2("Next Steps"),
    p("The audit team will track progress every quarter."),
    p("Next review is scheduled for 14 January 2027."),
  ]}]}), "06_header_footer.docx");

// source page for the scan
await save(new Document({ styles: { default: { document: { run: { font: "Arial", size: 28 } } } }, sections: [{ properties: { page: A4 }, children: [
  h1("Annual Summary 2026"),
  p("Kestrel Systems recorded revenue of ₹9,84,000."),
  p("The office in Coimbatore opened on 5 May 2026."),
  p("Reference number: SCN-3309"),
]}]}), "_scan_source.docx");
console.log("docx done");
})();
