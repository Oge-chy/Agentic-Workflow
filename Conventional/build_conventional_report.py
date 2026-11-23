from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import re

root = Path.cwd()
md_path = root / 'Conventional_Evaluation_Report.md'
out_path = root / 'Conventional_Evaluation_Report.docx'
text = md_path.read_text(encoding='utf-8').splitlines()
doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(0.68); sec.bottom_margin = Inches(0.65)
sec.left_margin = Inches(0.62); sec.right_margin = Inches(0.62)

# Clean report typography and hierarchy.
styles = doc.styles
normal = styles['Normal']; normal.font.name = 'Aptos'; normal.font.size = Pt(9.5); normal.font.color.rgb = RGBColor(35, 43, 52)
normal.paragraph_format.space_after = Pt(5); normal.paragraph_format.line_spacing = 1.08
for stylename, size, color in [('Title',25,'172B4D'),('Heading 1',16,'17365D'),('Heading 2',12,'1F4E79'),('Heading 3',10,'1F4E79')]:
    st=styles[stylename]; st.font.name='Aptos Display'; st.font.size=Pt(size); st.font.bold=True; st.font.color.rgb=RGBColor.from_string(color)
    st.paragraph_format.space_before=Pt(10 if stylename!='Title' else 0); st.paragraph_format.space_after=Pt(5)

# Small running footer for multi-page reading.
footer=sec.footer.paragraphs[0]
footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
rr=footer.add_run('Conventional workflow evaluation  |  '); rr.font.name='Aptos'; rr.font.size=Pt(8); rr.font.color.rgb=RGBColor(105,115,125)
field=OxmlElement('w:fldSimple'); field.set(qn('w:instr'),'PAGE'); footer._p.append(field)

def add_inline(paragraph, s):
    s=s.replace('<sub>z</sub>','z').replace('**','') if False else s
    s=s.replace('<sub>z</sub>','z')
    # Parse bold and italic Markdown spans into Word runs.
    pat=re.compile(r'(\*\*.*?\*\*|\*[^*]+\*)')
    pos=0
    for m in pat.finditer(s):
        if m.start()>pos: paragraph.add_run(s[pos:m.start()])
        token=m.group(0)
        if token.startswith('**'):
            r=paragraph.add_run(token[2:-2]); r.bold=True
        else:
            r=paragraph.add_run(token[1:-1]); r.italic=True
        pos=m.end()
    if pos<len(s): paragraph.add_run(s[pos:])

def shade(cell, fill):
    tcPr=cell._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),fill); tcPr.append(shd)

def set_cell_margins(cell, top=65, start=65, bottom=65, end=65):
    tc=cell._tc; tcPr=tc.get_or_add_tcPr(); mar=tcPr.first_child_found_in('w:tcMar')
    if mar is None: mar=OxmlElement('w:tcMar'); tcPr.append(mar)
    for m,v in [('top',top),('start',start),('bottom',bottom),('end',end)]:
        node=mar.find(qn('w:'+m))
        if node is None: node=OxmlElement('w:'+m); mar.append(node)
        node.set(qn('w:w'),str(v)); node.set(qn('w:type'),'dxa')

def add_table(headers, rows, font_size=8):
    table=doc.add_table(rows=1, cols=len(headers)); table.alignment=WD_TABLE_ALIGNMENT.CENTER; table.style='Table Grid'
    table.autofit=True
    for j,h in enumerate(headers):
        cell=table.rows[0].cells[j]; cell.text=''; shade(cell,'17365D'); cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER; set_cell_margins(cell)
        p=cell.paragraphs[0]; p.paragraph_format.space_after=Pt(0); p.paragraph_format.space_before=Pt(0)
        r=p.add_run(h); r.bold=True; r.font.name='Aptos'; r.font.size=Pt(font_size); r.font.color.rgb=RGBColor(255,255,255)
    # Repeat header on page breaks.
    trPr=table.rows[0]._tr.get_or_add_trPr(); repeat=OxmlElement('w:tblHeader'); repeat.set(qn('w:val'),'true'); trPr.append(repeat)
    for ix,row in enumerate(rows):
        cells=table.add_row().cells
        for j,val in enumerate(row):
            cells[j].text=str(val).strip(); cells[j].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER; set_cell_margins(cells[j],45,55,45,55)
            if ix%2==1: shade(cells[j],'F1F5F9')
            for p in cells[j].paragraphs:
                p.paragraph_format.space_after=Pt(0); p.paragraph_format.space_before=Pt(0); p.paragraph_format.line_spacing=1.0
                for r in p.runs: r.font.name='Aptos'; r.font.size=Pt(font_size); r.font.color.rgb=RGBColor(35,43,52)
    doc.add_paragraph().paragraph_format.space_after=Pt(1)
    return table

def split_md_row(line):
    return [x.strip() for x in line.strip().strip('|').split('|')]

def is_separator(line):
    return bool(re.fullmatch(r'[\s|:-]+', line)) and '-' in line

i=0
while i<len(text):
    line=text[i].strip()
    if not line:
        i+=1; continue
    if line.startswith('|'):
        table_lines=[]
        while i<len(text) and text[i].strip().startswith('|'):
            table_lines.append(text[i].strip()); i+=1
        parsed=[split_md_row(x) for x in table_lines if not is_separator(x)]
        if not parsed: continue
        headers=parsed[0]; rows=parsed[1:]
        if headers and headers[0]=='Base model' and 'Accuracy difference' in headers[1]:
            # Break the very wide three-metric comparison into readable portrait tables.
            for title,start in [('Accuracy',1),('F1',4),('AUROC',7)]:
                doc.add_heading(title,level=3)
                add_table(['Model','Difference','d_z','Exact p','Holm p'],[[r[0],r[start],r[start+1],r[start+2],'1.000'] for r in rows],font_size=8.5)
        else:
            add_table(headers,rows,font_size=7.8 if len(headers)>=7 else 8.5)
        continue
    if line.startswith('# '):
        p=doc.add_paragraph(style='Title'); add_inline(p,line[2:]); i+=1; continue
    if line.startswith('## '):
        doc.add_heading(line[3:],level=1); i+=1; continue
    if line.startswith('### '):
        doc.add_heading(line[4:],level=2); i+=1; continue
    if line.startswith('- '):
        p=doc.add_paragraph(style='List Bullet'); add_inline(p,line[2:]); i+=1; continue
    m=re.match(r'^\d+\.\s+(.*)',line)
    if m:
        p=doc.add_paragraph(style='List Number'); add_inline(p,m.group(1)); i+=1; continue
    p=doc.add_paragraph(); add_inline(p,line); i+=1

# Set document metadata.
doc.core_properties.title='Conventional Workflow Evaluation Report'
doc.core_properties.subject='Classification performance, efficiency, reproducibility, and failure analysis'
doc.core_properties.keywords='conventional workflow, classification, CV, reproducibility'
doc.save(out_path)
print(out_path)
