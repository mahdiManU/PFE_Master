from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.shared import Pt

def color_red_in_text(paragraph, words_to_color):
    for run in paragraph.runs:
        text = run.text
        for word in words_to_color:
            if word in text:
                text_parts = text.split(word)
                new_run = run._element
                run.text = text_parts[0]
                for part in text_parts[1:]:
                    colored_run = paragraph.add_run(word)
                    colored_run.font.color.rgb = RGBColor(255, 0, 0)  # Red color
                    paragraph.add_run(part)
def set_table_border(table):
    tbl = table._element
    tblPr = tbl.xpath('./w:tblPr')[0]
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), '000000')
        tblBorders.append(border)
    tblPr.append(tblBorders)
def generer_rapportENG(erreurs,nom_fichier):
  document = Document()
  erreurS = []
  erreurMI = []
  for i in erreurs:
     if("Erreur S" in i):
        erreurS.append(i)
     else : 
        erreurMI.append(i)
  style = document.styles['Normal']
  style.font.name = 'Calibri'
#style speciale 
  styleTitre = document.styles.add_style('CenteredTitle', WD_STYLE_TYPE.PARAGRAPH)
  styleTitre.font.size = Pt(24)  # Définir la taille de la police
  styleTitre.font.bold = True  # Mettre en gras
  styleTitre.font.underline = False  # Pas de soulignement
  styleTitre.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER  # Centrer le texte
  header_section = document.sections[0]
  header = header_section.header
  header_text = header.paragraphs[0]
  title = document.add_paragraph('Process Verification Report',style='CenteredTitle')
  title.alignment = WD_ALIGN_PARAGRAPH.CENTER
  p = document.add_paragraph("This document is a process audit report. It presents the verification results for three types of errors: errors due to missing information, structural errors and contradiction errors. Each type of error is illustrated by a table containing the error and its type, the law associated with this error and the corresponding recommendation.")
  document.add_heading('1- Errors due to missing information', level=1)
  table = document.add_table(rows=1, cols=4)

  hdr_cells = table.rows[0].cells
  hdr_cells[0].text = 'Error'
  hdr_cells[1].text = "Error type"
  hdr_cells[2].text = "Legal interpretation"
  hdr_cells[3].text = 'Recommendation'

  for cell in hdr_cells:
      for paragraph in cell.paragraphs:
          for run in paragraph.runs:
              run.bold = True

  for i in erreurMI:
     val = i.split("#")
     row_cells = table.add_row().cells
     row_cells[0].text =  val[0].replace('Erreur','Error')
        ##############
     if(val[1] == " Condition manquante "):
        row_cells[1].text = "Missing condition"
     if(val[1] == " Role manquant "):
        row_cells[1].text = "Missing Role"
        ####################
     if((val[1] == " Condition manquante ")):
         row_cells[2].text = "It happens when the condition is not mentioned in any of the legal texts. This is the problem of the legal incompleteness.Precisely the absence of a condition."
     if(val[1] == " Role manquant "):
         row_cells[2].text = "It happens when the role/organizational unit is not mentioned in any of the legal texts. This is the problem of the legal incompleteness. Precisely the absence of a role."
     row_cells[3].text = "This part is not annotated on the diagram"
     row_cells[0].width = Cm(1)
  set_table_border(table)
  document.add_heading('2- Structural Errors', level=1)
  tableS = document.add_table(rows=1, cols=4)

  hdr_cells = tableS.rows[0].cells
  hdr_cells[0].text = 'Error'
  hdr_cells[1].text = "Error type"
  hdr_cells[2].text = "Legal interpretation"
  hdr_cells[3].text = 'Recommendation'

  for cell in hdr_cells:
      for paragraph in cell.paragraphs:
          for run in paragraph.runs:
              run.bold = True
  
  for i in erreurS:
     val = i.split("#")
     row_cells = tableS.add_row().cells
     row_cells[0].text = val[0]
     row_cells[1].text = val[1]
     if(val[1] == " (Deterministic deadlock)"):
         row_cells[2].text= "the statement is ambiguous. This happens when there is the ambiguity associated with the use of ‘and’ and ‘or’"
     if(val[1] ==" (Deterministic lack of synchronization)"):
         row_cells[2].text = "If it is considered to be an 'inclusive or', it will be represented as an inclusive gateway, which is not a problem.On the contrary, if it is considered as an exclusive 'or', it will be represented by an exclusive gateway. This will lead to a situation of lack of synchronization."
     if(val[1] ==" (Nondeterministic lack of synchronization)"):
         row_cells[2].text = "The problem resides in the fact that the first ‘or’ is considered as an 'inclusive or', so it is represented as an inclusive gateway, however, the second ‘or’ is considered as an exclusive ‘or’, so it is represented as an exclusive gateway. This will lead to a situation of nondeterministic lack of synchronization."
     if(val[1] == " (Nondeterministic deadlock)"):
         row_cells[2].text = "Therefore the statement is ambiguous. This happens when there is the ambiguity associated with the use of ‘and’ and ‘or’. "
     row_cells[3].text = val[2]
     color_red_in_text(row_cells[3].paragraphs[0], ["and // or"])
     row_cells[0].width = Cm(1)
     print(erreurS.__str__())
     print(erreurMI.__str__())
  set_table_border(tableS)
  document.add_page_break()
  document.save(nom_fichier)


