from pathlib import Path
from xml.sax.saxutils import escape
import re
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

root=Path.cwd(); md_path=root/'Conventional_Evaluation_Report.md'
out_dir=root/'output'/'pdf'; out_dir.mkdir(parents=True,exist_ok=True)
out_path=out_dir/'Conventional_Evaluation_Report.pdf'
# Register Arial for reliable Windows and Unicode glyph rendering.
font_dir=Path(r'C:\Windows\Fonts')
pdfmetrics.registerFont(TTFont('Arial',str(font_dir/'arial.ttf')))
pdfmetrics.registerFont(TTFont('Arial-Bold',str(font_dir/'arialbd.ttf')))
pdfmetrics.registerFont(TTFont('Arial-Italic',str(font_dir/'ariali.ttf')))
pdfmetrics.registerFont(TTFont('Arial-BoldItalic',str(font_dir/'arialbi.ttf')))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-BoldItalic')

NAVY=colors.HexColor('#17365D'); BLUE=colors.HexColor('#1F4E79'); INK=colors.HexColor('#232B34'); MUTED=colors.HexColor('#586575'); PALE=colors.HexColor('#EEF3F8'); GRID=colors.HexColor('#D7DEE7'); TEAL=colors.HexColor('#0F6B78')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReportTitle',fontName='Arial-Bold',fontSize=22,leading=26,textColor=NAVY,spaceAfter=10,keepWithNext=True))
styles.add(ParagraphStyle(name='H1x',fontName='Arial-Bold',fontSize=15,leading=19,textColor=NAVY,spaceBefore=11,spaceAfter=5,keepWithNext=True))
styles.add(ParagraphStyle(name='H2x',fontName='Arial-Bold',fontSize=11.5,leading=15,textColor=BLUE,spaceBefore=8,spaceAfter=4,keepWithNext=True))
styles.add(ParagraphStyle(name='H3x',fontName='Arial-Bold',fontSize=9.5,leading=12,textColor=TEAL,spaceBefore=5,spaceAfter=3,keepWithNext=True))
styles.add(ParagraphStyle(name='Bodyx',fontName='Arial',fontSize=8.8,leading=12,textColor=INK,spaceAfter=5))
styles.add(ParagraphStyle(name='Bulletx',parent=styles['Bodyx'],leftIndent=13,firstLineIndent=-8,spaceAfter=3))
styles.add(ParagraphStyle(name='Meta',fontName='Arial',fontSize=8.4,leading=11,textColor=MUTED,spaceAfter=3))
styles.add(ParagraphStyle(name='TableHead',fontName='Arial-Bold',fontSize=7.1,leading=8.3,textColor=colors.white,alignment=TA_LEFT))
styles.add(ParagraphStyle(name='TableCell',fontName='Arial',fontSize=7.15,leading=8.5,textColor=INK))
styles.add(ParagraphStyle(name='TableCellSmall',fontName='Arial',fontSize=6.8,leading=8,textColor=INK))
styles.add(ParagraphStyle(name='Callout',fontName='Arial-Bold',fontSize=9,leading=12,textColor=NAVY,spaceAfter=0))


def md_inline(s):
    s=s.replace('<sub>z</sub>','z').replace('&','&amp;')
    # Escape angle brackets not used for supported tags; only simple Markdown formatting is present.
    s=escape(s, {'"':'&quot;'})
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'\*(.+?)\*',r'<i>\1</i>',s)
    s=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',s)
    # Undo ampersand double-escaping introduced by XML escaping order.
    return s.replace('&amp;amp;','&amp;')

def row_parts(line): return [x.strip() for x in line.strip().strip('|').split('|')]
def is_sep(line): return bool(re.fullmatch(r'[\s|:-]+',line)) and '-' in line

def make_table(headers,rows,small=False):
    avail=letter[0]-1.1*inch
    n=len(headers)
    if n==7: weights=[0.72,1.0,0.92,1.0,0.92,1.0,0.92]
    elif n==8: weights=[1.12,0.88,0.58,0.58,0.58,0.58,0.72,1.35]
    elif n==5: weights=[0.95,1.0,0.72,0.82,0.82]
    elif n==4: weights=[1.05,1.0,1.0,1.0]
    else: weights=[1.0]*n
    total=sum(weights); widths=[avail*w/total for w in weights]
    cellstyle=styles['TableCellSmall'] if small or n>=7 else styles['TableCell']
    data=[[Paragraph(md_inline(h),styles['TableHead']) for h in headers]]
    for row in rows:
        data.append([Paragraph(md_inline(str(v)),cellstyle) for v in row])
    tbl=Table(data,colWidths=widths,repeatRows=1,hAlign='CENTER',splitByRow=1)
    cmds=[('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.35,GRID),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]
    for r in range(2,len(data),2): cmds.append(('BACKGROUND',(0,r),(-1,r),PALE))
    tbl.setStyle(TableStyle(cmds)); return tbl

def on_page(canvas,doc):
    canvas.saveState(); w,h=letter
    canvas.setStrokeColor(GRID); canvas.setLineWidth(.5)
    canvas.line(.55*inch,.48*inch,w-.55*inch,.48*inch)
    canvas.setFont('Arial',7.5); canvas.setFillColor(MUTED)
    canvas.drawString(.58*inch,.31*inch,'Conventional workflow evaluation')
    canvas.drawRightString(w-.58*inch,.31*inch,f'{doc.page}')
    if doc.page>1:
        canvas.setFont('Arial-Bold',7.4); canvas.setFillColor(BLUE)
        canvas.drawRightString(w-.58*inch,h-.38*inch,'RESULTS REPORT')
    canvas.restoreState()

doc=SimpleDocTemplate(str(out_path),pagesize=letter,rightMargin=.55*inch,leftMargin=.55*inch,topMargin=.62*inch,bottomMargin=.62*inch,title='Conventional Workflow Evaluation Report',author='OpenAI',subject='Classification performance, efficiency, reproducibility, and failure analysis')
story=[]
lines=md_path.read_text(encoding='utf-8').splitlines(); i=0; first_content=True
while i<len(lines):
    raw=lines[i]; line=raw.strip()
    if not line: i+=1; continue
    if line.startswith('|'):
        group=[]
        while i<len(lines) and lines[i].strip().startswith('|'):
            group.append(lines[i].strip()); i+=1
        parsed=[row_parts(x) for x in group if not is_sep(x)]
        if not parsed: continue
        headers,rows=parsed[0],parsed[1:]
        if headers and headers[0]=='Base model' and 'Accuracy difference' in headers[1]:
            for title,start in [('Accuracy',1),('F1',4),('AUROC',7)]:
                story.append(Paragraph(title,styles['H3x']))
                story.append(make_table(['Model','Difference','d_z','Exact p','Holm p'],[[r[0],r[start],r[start+1],r[start+2],'1.000'] for r in rows],small=True))
                story.append(Spacer(1,4))
        else:
            story.append(make_table(headers,rows,small=len(headers)>=7))
            story.append(Spacer(1,6))
        continue
    if line.startswith('# '):
        title=line[2:]
        story.append(Paragraph(md_inline(title),styles['ReportTitle']))
        i+=1; continue
    if line.startswith('## '): story.append(Paragraph(md_inline(line[3:]),styles['H1x'])); i+=1; continue
    if line.startswith('### '):
        if line[4:] in ('Held-out test results','D. Failure and risk analysis'):
            story.append(PageBreak())
        story.append(Paragraph(md_inline(line[4:]),styles['H2x'])); i+=1; continue
    if line.startswith('**Source:**') or line.startswith('**Dataset split:**') or line.startswith('**Repeated CV seeds:**') or line.startswith('**Date of report:**'):
        story.append(Paragraph(md_inline(line),styles['Meta'])); i+=1; continue
    if line.startswith('- '):
        story.append(Paragraph('- '+md_inline(line[2:]),styles['Bulletx'])); i+=1; continue
    m=re.match(r'^\d+\.\s+(.*)',line)
    if m:
        story.append(Paragraph(md_inline(m.group(1)),styles['Bulletx'])); i+=1; continue
    story.append(Paragraph(md_inline(line),styles['Bodyx'])); i+=1

doc.build(story,onFirstPage=on_page,onLaterPages=on_page)
print(out_path)
