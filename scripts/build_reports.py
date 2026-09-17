#!/usr/bin/env python3
"""Build the two practice reports from the college-provided DOCX templates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
REPORTS = ROOT / "reports"
REPO = "https://github.com/crankoff/PP_09.02.07"
CATALOG = "https://github.com/practical-tutorials/project-based-learning#react"
DEPLOY = "https://render.com/deploy?repo=https://github.com/crankoff/PP_09.02.07"
DEMO = f"{REPO}/blob/main/docs/demo/flowboard-demo.gif"
LOCAL = "http://localhost:8000"


@dataclass(frozen=True)
class ReportSpec:
    code: str
    module: str
    period: str
    accepted: str
    template: Path
    filename: str
    competencies: tuple[tuple[str, str], ...]
    diary: tuple[tuple[str, str, str], ...]
    emphasis: str


PM02 = ReportSpec(
    code="ПМ.02",
    module="Осуществление интеграции программных модулей",
    period="25.05.2026–14.06.2026",
    accepted="25 мая 2026 г.",
    template=WORKSPACE / "Шаблон_отчета_по_практике (3) (1).docx",
    filename="Отчет_ПМ02_FlowBoard.docx",
    competencies=(
        ("ПК 2.1", "Разрабатывать требования к программным модулям на основе анализа проектной и технической документации на предмет взаимодействия компонент"),
        ("ПК 2.2", "Выполнять интеграцию модулей в программное обеспечение"),
        ("ПК 2.3", "Выполнять отладку программного модуля с использованием специализированных программных средств"),
        ("ПК 2.4", "Осуществлять разработку тестовых наборов и тестовых сценариев для программного обеспечения"),
        ("ПК 2.5", "Производить инспектирование компонент программного обеспечения на предмет соответствия стандартам кодирования"),
    ),
    diary=(
        ("25.05.2026", "8", "Проанализированы требования задания и каталог проектов; выбрана канбан-доска FlowBoard."),
        ("26.05.2026", "8", "Сформированы функциональные и нефункциональные требования, роли и критерии приемки."),
        ("27.05.2026", "8", "Спроектированы границы frontend, HTTP-, сервисного и database-модулей."),
        ("28.05.2026", "8", "Описан REST API и контракты взаимодействия модулей."),
        ("29.05.2026", "8", "Интегрированы маршрутизация, сервисный слой, SQLite и статический frontend."),
        ("01.06.2026", "8", "Интегрированы регистрация, вход, подписанная сессия и CSRF-защита."),
        ("02.06.2026", "4", "Интегрированы карточки задач, поиск, фильтр и статистика."),
        ("03.06.2026", "8", "Выполнена отладка CRUD-операций и обработки ошибок API."),
        ("04.06.2026", "8", "Проверены drag-and-drop, кнопки перемещения и адаптивная верстка."),
        ("05.06.2026", "4", "Исправлена обработка конкурентного обновления по полю version."),
        ("08.06.2026", "8", "Проверены security headers, ограничение запросов и изоляция данных."),
        ("09.06.2026", "8", "Разработаны модульные тесты безопасности и сервисного слоя."),
        ("10.06.2026", "8", "Разработаны интеграционные HTTP-тесты и проверен полный сценарий."),
        ("11.06.2026", "8", "Проведено инспектирование структуры, именования, SQL и обработки исключений."),
        ("12.06.2026", "4", "Подготовлены CI, README, диаграммы, GIF и итоговая документация."),
    ),
    emphasis="интеграцию программных модулей, отладку и автоматизированное тестирование",
)


PM11 = ReportSpec(
    code="ПМ.11",
    module="Разработка, администрирование и защита баз данных",
    period="15.06.2026–28.06.2026",
    accepted="15 июня 2026 г.",
    template=WORKSPACE / "Отчетная документация по ПП ПМ11 (2) (6) (1).docx",
    filename="Отчет_ПМ11_FlowBoard.docx",
    competencies=(
        ("ПК 11.1", "Осуществлять сбор, обработку и анализ информации для проектирования баз данных"),
        ("ПК 11.2", "Проектировать базу данных на основе анализа предметной области"),
        ("ПК 11.3", "Разрабатывать объекты базы данных в соответствии с результатами анализа предметной области"),
        ("ПК 11.4", "Реализовывать базу данных в конкретной системе управления базами данных"),
        ("ПК 11.5", "Администрировать базы данных"),
        ("ПК 11.6", "Защищать информацию в базе данных с использованием технологии защиты информации"),
    ),
    diary=(
        ("15.06.2026", "8", "Собраны требования к данным, ролям, операциям и журналированию FlowBoard."),
        ("16.06.2026", "8", "Построена концептуальная модель: users, tasks, activities, schema_migrations."),
        ("17.06.2026", "8", "Выполнена нормализация до 3НФ, определены ключи и связи."),
        ("18.06.2026", "6", "Разработана SQL-миграция таблиц, ограничений и внешних ключей."),
        ("19.06.2026", "6", "Добавлены индексы, CHECK/UNIQUE-ограничения и тестовые данные."),
        ("22.06.2026", "8", "Реализованы параметризованные CRUD-запросы и транзакции SQLite."),
        ("23.06.2026", "8", "Реализованы команды миграции, статистики и integrity_check."),
        ("24.06.2026", "8", "Реализованы online backup и контролируемое восстановление БД."),
        ("25.06.2026", "6", "Настроены scrypt, HMAC-сессии, CSRF и проверка владельца записи."),
        ("26.06.2026", "6", "Проверены целостность, изоляция пользователей, backup/restore и документация."),
    ),
    emphasis="проектирование, реализацию, администрирование и защиту базы данных",
)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_text(cell, text: str, *, bold: bool = False, size: float = 9, align=None) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    if align is not None:
        p.alignment = align
    r = p.add_run(str(text))
    r.bold = bold
    r.font.name = "Times New Roman"
    r.font.size = Pt(size)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_cell_margins(cell, top=70, start=90, bottom=70, end=90) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def dont_split_row(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tr_pr.append(OxmlElement("w:cantSplit"))


def add_hyperlink(paragraph, text: str, url: str, *, size: float = 9.5) -> None:
    relation = paragraph.part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), relation)
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    size_node = OxmlElement("w:sz")
    size_node.set(qn("w:val"), str(int(size * 2)))
    font = OxmlElement("w:rFonts")
    font.set(qn("w:ascii"), "Times New Roman")
    font.set(qn("w:hAnsi"), "Times New Roman")
    props.extend((font, color, underline, size_node))
    text_node = OxmlElement("w:t")
    text_node.text = text
    run.extend((props, text_node))
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def clean_template(path: Path) -> Document:
    doc = Document(path)
    body = doc._element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)
    return doc


def configure_styles(doc: Document) -> None:
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.widow_control = True

    title = styles["Title"]
    title.font.name = "Times New Roman"
    title.font.size = Pt(18)
    title.font.bold = True
    title.font.color.rgb = RGBColor(0, 0, 0)
    title.paragraph_format.space_after = Pt(12)

    for name, size in (("Heading 1", 15), ("Heading 2", 13), ("Heading 3", 11.5)):
        style = styles[name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(31, 56, 79)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.space_before = Pt(9)
        style.paragraph_format.space_after = Pt(5)


def add_page_break(doc: Document) -> None:
    # A break in an empty run can create a blank page when the preceding page is
    # completely full. A paragraph that itself starts on the next page is stable.
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = True
    p.paragraph_format.space_after = Pt(0)


def add_para(doc: Document, text: str = "", *, bold=False, align=None, size=None, indent=True, space_after=5, justify=True):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    elif indent:
        p.paragraph_format.first_line_indent = Cm(1.25)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if justify else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(space_after)
    r = p.add_run(text)
    r.bold = bold
    r.font.name = "Times New Roman"
    if size:
        r.font.size = Pt(size)
    return p


def add_center(doc: Document, text: str, *, bold=False, size=11, after=4):
    return add_para(doc, text, bold=bold, align=WD_ALIGN_PARAGRAPH.CENTER, size=size, indent=False, space_after=after)


def add_labeled_link(doc: Document, label: str, text: str, url: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.space_after = Pt(5)
    r = p.add_run(f"{label}: ")
    r.bold = True
    r.font.name = "Times New Roman"
    add_hyperlink(p, text, url, size=10.5)


def add_table(doc: Document, headers: Iterable[str], rows: Iterable[Iterable[str]], widths=None, font_size=8.5):
    headers = list(headers)
    rows = [list(row) for row in rows]
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    table.autofit = False
    hdr = table.rows[0]
    repeat_table_header(hdr)
    for idx, text in enumerate(headers):
        set_cell_text(hdr.cells[idx], text, bold=True, size=font_size, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_shading(hdr.cells[idx], "D9EAF0")
    for row_data in rows:
        row = table.add_row()
        dont_split_row(row)
        for idx, value in enumerate(row_data):
            set_cell_text(row.cells[idx], str(value), size=font_size)
    if widths:
        for idx, width in enumerate(widths):
            table.columns[idx].width = Cm(width)
        for row in table.rows:
            for idx, width in enumerate(widths):
                row.cells[idx].width = Cm(width)
    for row in table.rows:
        for cell in row.cells:
            set_cell_margins(cell)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_kv_table(doc: Document, rows: Iterable[tuple[str, str]], widths=(5.0, 11.5), font_size=9.5):
    table = doc.add_table(rows=0, cols=2)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Cm(widths[0])
    table.columns[1].width = Cm(widths[1])
    for label, value in rows:
        row = table.add_row()
        dont_split_row(row)
        set_cell_text(row.cells[0], label, bold=True, size=font_size)
        set_cell_shading(row.cells[0], "EAF2F5")
        set_cell_text(row.cells[1], value, size=font_size)
        row.cells[0].width = Cm(widths[0])
        row.cells[1].width = Cm(widths[1])
        for cell in row.cells:
            set_cell_margins(cell)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_bullets(doc: Document, values: Iterable[str]) -> None:
    for value in values:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.7)
        p.paragraph_format.first_line_indent = Cm(-0.3)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(f"• {value}")
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)


def add_picture(doc: Document, path: Path, caption: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(path), width=Inches(6.25))
    caption_p = doc.add_paragraph()
    caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption_p.paragraph_format.space_after = Pt(7)
    r = caption_p.add_run(caption)
    r.italic = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(9.5)


def add_official_header(doc: Document) -> None:
    add_center(doc, "Автономная некоммерческая профессиональная образовательная организация", bold=True, size=10)
    add_center(doc, "«Хекслет колледж»", bold=True, size=11)


def add_title_page(doc: Document, spec: ReportSpec) -> None:
    add_official_header(doc)
    for _ in range(4):
        doc.add_paragraph()
    add_center(doc, "ОТЧЕТНАЯ ДОКУМЕНТАЦИЯ", bold=True, size=17, after=10)
    add_center(doc, f"по производственной практике {spec.code}", bold=True, size=14, after=26)
    add_kv_table(doc, (
        ("Специальность", "09.02.07 Информационные системы и программирование"),
        (spec.code, spec.module),
        ("Студент", "____________________________________________________"),
        ("Курс", "________________"),
        ("Группа №", "________________"),
        ("Период практики", spec.period),
    ), font_size=10)
    doc.add_paragraph()
    add_para(doc, "Место прохождения практики: АНПОО «Хекслет колледж»", indent=False, size=10.5)
    add_para(doc, "Адрес: ____________________________________________________________", indent=False, size=10.5)
    for _ in range(5):
        doc.add_paragraph()
    add_center(doc, "Санкт-Петербург", size=11)
    add_center(doc, "2026 г.", size=11)


def add_assignment(doc: Document, spec: ReportSpec) -> None:
    add_page_break(doc)
    add_official_header(doc)
    add_center(doc, "ЗАДАНИЕ", bold=True, size=16, after=7)
    add_center(doc, f"на производственную практику {spec.code}", bold=True, size=13, after=10)
    add_kv_table(doc, (
        ("Для обучающегося", "____________________________________________________"),
        ("Специальность", "09.02.07 Информационные системы и программирование"),
        ("Курс / группа", "________________ / ________________"),
        (spec.code, spec.module),
        ("Место практики", "АНПОО «Хекслет колледж»"),
        ("Период", spec.period),
    ), font_size=9.5)
    add_para(doc, f"Цель практики: разработка и представление проекта в рамках профессионального модуля {spec.code} «{spec.module}».", bold=True)
    add_para(doc, "Задание на практику:", bold=True, indent=False)
    add_bullets(doc, [description for _, description in spec.competencies])
    add_para(doc, "Индивидуальная часть: разработать веб-приложение FlowBoard, обеспечить документированные интерфейсы, целостность данных, безопасность, тестирование и воспроизводимый запуск.", indent=False, justify=False, space_after=10)
    for _ in range(2):
        doc.add_paragraph()
    add_para(doc, f"Задание принято к исполнению ___________________________ «{spec.accepted}»", indent=False)
    add_para(doc, "                                                      подпись обучающегося", indent=False, size=9)


def add_diary(doc: Document, spec: ReportSpec) -> None:
    add_page_break(doc)
    add_official_header(doc)
    add_center(doc, "ДНЕВНИК", bold=True, size=16)
    add_center(doc, f"прохождения производственной практики {spec.code}", bold=True, size=12, after=8)
    add_kv_table(doc, (
        ("ФИО обучающегося", "____________________________________________________"),
        ("Курс / группа", "________________ / ________________"),
        ("Вид практики", "Производственная"),
        ("Место практики", "АНПОО «Хекслет колледж»"),
        ("Период", spec.period),
    ), font_size=8.5)
    add_center(doc, "Учет выполняемой работы", bold=True, size=11, after=5)
    diary_rows = []
    for idx, (date, hours, work) in enumerate(spec.diary, 1):
        diary_rows.append((idx, work, date, hours, ""))
    diary_rows.append(("", "", "Всего", "72", ""))
    add_table(
        doc,
        ("№", "Содержание работы", "Дата", "Часы", "Подпись"),
        diary_rows,
        widths=(0.8, 10.0, 2.4, 1.2, 2.0),
        font_size=7.2 if spec.code == "ПМ.02" else 7.8,
    )


def add_attestation(doc: Document, spec: ReportSpec) -> None:
    add_page_break(doc)
    add_official_header(doc)
    add_center(doc, "АТТЕСТАЦИОННЫЙ ЛИСТ", bold=True, size=15)
    add_center(doc, f"по итогам прохождения производственной практики {spec.code}", bold=True, size=11, after=7)
    add_kv_table(doc, (
        ("На обучающегося", "____________________________________________________"),
        ("Специальность", "09.02.07 Информационные системы и программирование"),
        ("Курс / группа", "________________ / ________________"),
        (spec.code, spec.module),
        ("Место / период", f"АНПОО «Хекслет колледж», {spec.period}"),
    ), font_size=8.3)
    add_center(doc, "Результаты освоения профессиональных компетенций", bold=True, size=10.5, after=4)
    rows = [(code, text, "□", "□", "□") for code, text in spec.competencies]
    add_table(doc, ("Код", "Компетенция", "Низкий", "Средний", "Высокий"), rows,
              widths=(1.6, 10.4, 1.4, 1.5, 1.5), font_size=7.8)
    add_para(doc, "Критерии: низкий уровень — работа под непосредственным руководством; средний — при периодическом консультировании; высокий — самостоятельное выполнение в соответствии с требованиями.", indent=False, size=8.5)
    add_para(doc, f"Общая оценка за производственную практику по {spec.code}: ___________________________", indent=False, size=10)
    add_para(doc, "Руководитель практики от профильной организации", indent=False, size=10)
    add_para(doc, "_______________________________  (__________________________)     М.П.", indent=False, size=10)
    add_para(doc, "                    ФИО                              подпись", indent=False, size=8.5)


COMMON_COMPETENCIES = (
    ("ОК 01", "Выбирать способы решения задач профессиональной деятельности применительно к различным контекстам"),
    ("ОК 02", "Осуществлять поиск, анализ и интерпретацию информации, необходимой для выполнения профессиональных задач"),
    ("ОК 03", "Планировать и реализовывать собственное профессиональное и личностное развитие"),
    ("ОК 04", "Работать в коллективе и команде, эффективно взаимодействовать с коллегами и руководством"),
    ("ОК 05", "Осуществлять устную и письменную коммуникацию на государственном языке"),
    ("ОК 09", "Использовать информационные технологии в профессиональной деятельности"),
    ("ОК 10", "Пользоваться профессиональной документацией на государственном и иностранном языках"),
)


def add_characteristic(doc: Document, spec: ReportSpec) -> None:
    add_page_break(doc)
    add_official_header(doc)
    add_center(doc, "ХАРАКТЕРИСТИКА", bold=True, size=16, after=8)
    add_kv_table(doc, (
        ("Обучающийся", "____________________________________________________"),
        ("Курс / группа", "________________ / ________________"),
        (spec.code, spec.module),
        ("Место / период", f"АНПОО «Хекслет колледж», {spec.period}"),
    ), font_size=9)
    add_para(doc, "За время производственной практики обучающийся освоил(а):", bold=True, indent=False)
    for code, description in spec.competencies:
        add_para(doc, f"{code}. {description}.", indent=False, size=9.5, space_after=2)
    add_para(doc, "Результаты освоения общих компетенций:", bold=True, indent=False)
    add_table(doc, ("Код", "Общая компетенция", "Результат (+/−)"),
              [(code, text, "") for code, text in COMMON_COMPETENCIES],
              widths=(1.7, 12.8, 2.0), font_size=8.2)
    add_para(doc, f"Заключение: обучающийся __________________________________ готов(а) к выполнению профессиональной деятельности по модулю «{spec.module}».", indent=False, size=9.5)
    add_para(doc, "Руководитель практики _______________________________ (___________________)     М.П.", indent=False, size=9.5)


def add_report_cover(doc: Document, spec: ReportSpec) -> None:
    add_page_break(doc)
    add_official_header(doc)
    for _ in range(5):
        doc.add_paragraph()
    add_center(doc, "ОТЧЕТ", bold=True, size=20, after=10)
    add_center(doc, f"о прохождении производственной практики по {spec.code}", bold=True, size=14)
    add_center(doc, f"«{spec.module}»", bold=True, size=13, after=22)
    add_center(doc, "Проект: FlowBoard — персональная канбан-доска", bold=True, size=14, after=20)
    add_kv_table(doc, (
        ("Обучающийся", "____________________________________________________"),
        ("Курс / группа", "________________ / ________________"),
        ("Руководитель", "____________________________________________________"),
        ("Период", spec.period),
        ("Репозиторий", REPO),
    ), font_size=9.5)
    for _ in range(4):
        doc.add_paragraph()
    add_center(doc, "Санкт-Петербург", size=11)
    add_center(doc, "2026 г.", size=11)
    # The cover always has ample free space, so a hard break here is stable and
    # keeps the first practical section on a fresh page.
    doc.add_page_break()


def add_selected_project(doc: Document, spec: ReportSpec) -> None:
    doc.add_heading("1. Выбранный проект", level=1)
    add_para(doc, "Название проекта: FlowBoard — персональная канбан-доска.", bold=True, indent=False)
    add_labeled_link(doc, "Проект из каталога", "Create a Trello Clone", CATALOG)
    add_para(doc, "FlowBoard помогает планировать учебные и личные задачи по канбан-методу. Пользователь регистрируется, создает карточки, назначает приоритет и срок, перемещает задачи между этапами «План», «В работе» и «Готово», применяет поиск и фильтр. В интерфейсе отображаются сводные показатели и журнал последних действий. Данные разных аккаунтов изолированы. Проект рассчитан на индивидуальное использование и демонстрирует полный цикл от требований и схемы данных до тестов и развертывания.", justify=False)
    add_para(doc, f"В рамках {spec.code} основной акцент сделан на {spec.emphasis}.", justify=False)
    add_para(doc, "Реализовано в ходе практики:", bold=True, indent=False)
    add_bullets(doc, (
        "модульная архитектура frontend → HTTP API → сервисный слой → SQLite;",
        "регистрация, вход и выход с безопасным хранением паролей;",
        "CRUD карточек, статусы, приоритеты, сроки и optimistic locking;",
        "drag-and-drop, кнопки перемещения, поиск, фильтр и адаптивный интерфейс;",
        "статистика, журналирование действий и изоляция данных пользователей;",
        "версионируемая SQL-миграция, индексы, ограничения и транзакции;",
        "CLI для миграций, контроля целостности, статистики, backup и restore;",
        "контракт OpenAPI, 17 автотестов, CI, Docker и Render Blueprint;",
        "README, архитектурные диаграммы и анимированная демонстрация.",
    ))


def add_technical_passport(doc: Document) -> None:
    doc.add_heading("2. Технический паспорт проекта", level=1)
    rows = (
        ("Название проекта", "FlowBoard"),
        ("Каталог", CATALOG),
        ("GitHub-репозиторий", REPO),
        ("Локальный адрес", LOCAL),
        ("Публичный деплой", "Render Blueprint подготовлен; экземпляр создается владельцем репозитория"),
        ("Frontend", "HTML5, CSS3, JavaScript ES2022, Fetch API, Drag and Drop API"),
        ("Backend", "Python 3.12, ThreadingHTTPServer, модульная сервисная архитектура"),
        ("База данных", "SQLite 3, SQL-миграции, FK/CHECK/UNIQUE, WAL, индексы"),
        ("Авторизация", "Да: scrypt, HMAC-SHA256, HttpOnly/SameSite cookie, CSRF"),
        ("Тестовый вход", "login: demo@example.com   password: Demo123!"),
        ("Тесты", "17 unittest: security, service, HTTP API; запуск в GitHub Actions"),
    )
    add_kv_table(doc, rows, font_size=9)
    add_labeled_link(doc, "Создание демо на Render", "Deploy to Render", DEPLOY)
    add_para(doc, "Примечание: ссылка Render создает новый сервис в аккаунте владельца. В бесплатной конфигурации файловая система эфемерна, поэтому для долговременного хранения нужен persistent disk и DATABASE_PATH=/var/data/flowboard.db.", indent=False, size=9.5)


def add_architecture(doc: Document, spec: ReportSpec) -> None:
    doc.add_heading("3. Архитектура проекта", level=1)
    doc.add_heading("3.1. Общая архитектурная схема", level=2)
    add_picture(doc, ROOT / "docs/diagrams/architecture.png", "Рисунок 1 — Архитектура FlowBoard")
    add_para(doc, "Браузер получает HTML, CSS и JavaScript с того же HTTP-сервера и обращается к REST API в формате JSON. HTTP-слой отвечает за маршрутизацию, ограничение размера запроса, cookie, security headers, аутентификацию и CSRF-проверку. После проверки запрос передается в BoardService, где сосредоточены валидация, права доступа и бизнес-правила. Database открывает соединения SQLite, применяет PRAGMA и миграции. Изменение задачи и запись в журнал выполняются в одной транзакции. CLI db_admin использует тот же database-модуль для проверки целостности и резервного копирования. Такое разделение упрощает тестирование и исключает прямое обращение frontend к БД.", justify=False)
    if spec.code == "ПМ.02":
        add_para(doc, "Интеграционный контракт зафиксирован на трех границах: Fetch/JSON между UI и HTTP; вызовы методов между HTTP и BoardService; параметризованный SQL между BoardService и Database.\u00a0Ошибки переводятся в единый JSON-формат и соответствующие HTTP-коды.", justify=False)
    else:
        add_para(doc, "В ПМ.11 особое внимание уделено тому, чтобы HTTP-слой не формировал SQL. Все обращения к данным проходят через сервис, включают user_id и выполняются в контролируемых транзакциях.", justify=False)

    doc.add_heading("3.2. Модель данных (ERD)", level=2)
    add_picture(doc, ROOT / "docs/diagrams/erd.png", "Рисунок 2 — ER-модель FlowBoard")
    add_table(doc, ("Сущность", "Назначение", "Ключевые ограничения"), (
        ("users", "Учетные записи", "email UNIQUE NOCASE; role CHECK; password_hash NOT NULL"),
        ("tasks", "Карточки пользователя", "user_id FK CASCADE; status/priority CHECK; version ≥ 1"),
        ("activities", "Аудит действий", "user_id FK CASCADE; task_id FK SET NULL"),
        ("schema_migrations", "Примененные миграции", "имя миграции — PRIMARY KEY"),
    ), widths=(3.2, 6.2, 7.0), font_size=8.5)
    add_para(doc, "Схема соответствует третьей нормальной форме: поля атомарны, данные аккаунта не дублируются в задачах, журнал отделен от текущего состояния карточки. Связи задаются внешними ключами. Индекс idx_tasks_user_status_position ускоряет основную выборку колонок, а idx_activities_user_created — получение последних событий.", justify=False)

    doc.add_heading("3.3. Use Case", level=2)
    add_picture(doc, ROOT / "docs/diagrams/use-case.png", "Рисунок 3 — Варианты использования")
    add_table(doc, ("Сценарий", "Основной успешный путь"), (
        ("UC-01 Вход", "Ввести email и пароль → проверить scrypt-хеш → получить подписанную cookie и CSRF → загрузить доску."),
        ("UC-02 Создание", "Открыть форму → заполнить карточку → POST /api/tasks → транзакция task + activity → обновить UI."),
        ("UC-03 Перемещение", "Перетащить карточку или нажать стрелку → PUT с status и version → проверить владельца → показать новый этап."),
        ("UC-04 Backup", "Запустить db_admin.py backup → Online Backup API → integrity_check копии → получить путь файла."),
    ), widths=(4.0, 12.5), font_size=8.7)

    doc.add_heading("3.4. REST API", level=2)
    add_labeled_link(doc, "Полный контракт", "openapi.yaml", f"{REPO}/blob/main/openapi.yaml")
    add_table(doc, ("Метод", "URL", "Назначение", "Результат"), (
        ("GET", "/api/health", "Проверка готовности", "200 {status: ok}"),
        ("GET", "/api/session", "Текущая сессия", "user, csrfToken"),
        ("POST", "/api/register", "Регистрация", "201 user + cookie"),
        ("POST", "/api/login", "Вход", "200 user + cookie"),
        ("POST", "/api/logout", "Выход", "204 + clear cookie"),
        ("GET", "/api/tasks", "Список/поиск/фильтр", "200 tasks[]"),
        ("POST", "/api/tasks", "Создание карточки", "201 task"),
        ("PUT", "/api/tasks/{id}", "Обновление/перемещение", "200 task / 409 conflict"),
        ("DELETE", "/api/tasks/{id}", "Удаление", "204"),
        ("GET", "/api/stats", "Сводные показатели", "200 counts"),
        ("GET", "/api/activity", "Последние действия", "200 activities[]"),
    ), widths=(1.7, 4.0, 6.2, 4.5), font_size=7.7)


def add_traceability(doc: Document, spec: ReportSpec) -> None:
    doc.add_heading("4. Таблица соответствия (трассировка реализации)", level=1)
    add_para(doc, "Ссылки указывают на конкретные файлы основной ветки. Экран приложения доступен локально после запуска; GIF в репозитории подтверждает основной пользовательский сценарий.", indent=False)
    trace = (
        ("Регистрация и вход", "kanban/security.py; kanban/web.py", "/api/register, /api/login"),
        ("Создание и редактирование", "kanban/service.py; public/app.js", "диалог задачи / API"),
        ("Перемещение по статусам", "public/app.js; kanban/service.py", "канбан-доска"),
        ("Поиск и фильтр", "public/app.js; kanban/service.py", "панель управления"),
        ("Статистика и журнал", "kanban/service.py; public/index.html", "верхние счетчики / журнал"),
        ("Схема и миграции", "migrations/001_initial.sql; kanban/database.py", "SQLite"),
        ("Backup / restore", "scripts/db_admin.py", "командная строка"),
        ("API-контракт", "openapi.yaml; kanban/web.py", "REST API"),
        ("Автотесты", "tests/test_api.py; tests/test_service.py", "GitHub Actions"),
        ("Развертывание", "Dockerfile; render.yaml", "Render Blueprint"),
    )
    table = add_table(doc, ("Функция", "Файл/папка в GitHub", "Экран/интерфейс"), trace,
                      widths=(4.0, 8.2, 4.3), font_size=8.1)
    for row_idx, (_, files, _) in enumerate(trace, 1):
        cell = table.rows[row_idx].cells[1]
        cell.text = ""
        p = cell.paragraphs[0]
        for i, file_path in enumerate(files.split("; ")):
            if i:
                p.add_run("; ")
            add_hyperlink(p, file_path, f"{REPO}/blob/main/{file_path}", size=8.1)
    if spec.code == "ПМ.02":
        add_para(doc, "Трассировка показывает, что каждый пользовательский сценарий проходит через несколько интегрированных модулей, а отдельные проверки закреплены в тестах и CI.")
    else:
        add_para(doc, "Для операций с данными отдельно прослеживаются SQL-схема, database-модуль, сервисные проверки и административная утилита.")


def add_demo_and_quality(doc: Document) -> None:
    doc.add_heading("5. Демонстрация работы", level=1)
    add_picture(doc, ROOT / "docs/demo/flowboard-report.png", "Рисунок 4 — Основной экран FlowBoard")
    add_labeled_link(doc, "Формат", "анимированный GIF в README", DEMO)
    add_para(doc, "Демонстрация показывает вход под тестовой учетной записью, создание карточки «Сдать производственную практику», открытие формы редактирования и перенос задачи из «План» в «В работе». Изменение сразу отражается в счетчиках и журнале. Для воспроизведения локально достаточно Python 3.12 и команды python3 app.py.")

    doc.add_heading("6. Репозиторий и качество кода", level=1)
    add_table(doc, ("Критерий", "Состояние", "Подтверждение"), (
        ("README: описание, стек, запуск", "Да", "README.md"),
        ("Открытый GitHub-репозиторий", "Да", REPO),
        ("Автотесты", "Да", "17 тестов: security, service, HTTP"),
        ("CI", "Да", ".github/workflows/ci.yml"),
        ("Демонстрация", "Да", "docs/demo/flowboard-demo.gif"),
        ("Code Climate", "Не подключен", "требует регистрации репозитория во внешнем сервисе"),
        ("История коммитов", "Да", "тематические коммиты по коду, тестам и документации"),
        ("Деплой", "Подготовлен", "Dockerfile + render.yaml; публикация через аккаунт владельца"),
    ), widths=(5.0, 3.0, 8.5), font_size=8.7)
    add_para(doc, "Код разделен по ответственности: конфигурация, безопасность, БД, сервисный слой и HTTP. SQL-параметры не конкатенируются с пользовательским вводом. Изменяющие запросы проверяют CSRF, а доступ к записи всегда ограничен user_id. Непредвиденные ошибки не возвращают внутренний стек клиенту. Внешние runtime-зависимости отсутствуют, что уменьшает поверхность поставки.", justify=False)
    add_para(doc, "Перед сдачей выполнены python -m compileall, 17 unittest, integrity_check, резервное копирование и восстановление тестовой БД. В браузере проверены основной сценарий, адаптивная ширина 390 px и отсутствие сообщений console error/warning.", justify=False)


def add_pm11_database_details(doc: Document) -> None:
    doc.add_heading("6.1. Реализация и администрирование БД", level=2)
    add_para(doc, "Миграция 001_initial.sql создает таблицы, ограничения и индексы идемпотентно. Database сравнивает имена SQL-файлов с schema_migrations и применяет только отсутствующие версии внутри транзакции. При каждом соединении включаются foreign_keys, busy_timeout и WAL. Это дает воспроизводимую схему и контролируемое обновление.", justify=False)
    add_para(doc, "Команда check выполняет PRAGMA integrity_check. Команда backup применяет SQLite Online Backup API и создает согласованную копию даже при доступности исходной БД. Restore требует явный флаг --force, заранее проверяет целостность копии и должен запускаться при остановленном веб-сервере. Stats выводит количество пользователей, задач и событий для оперативного контроля.", justify=False)
    add_table(doc, ("Угроза", "Реализованная мера"), (
        ("SQL injection", "Параметризованные запросы; динамичны только фиксированные фрагменты."),
        ("Чтение чужих задач", "Каждый SELECT/UPDATE/DELETE включает user_id текущей сессии."),
        ("Утечка пароля", "scrypt с индивидуальной 128-битной солью; пароль не хранится."),
        ("Нарушение целостности", "FOREIGN KEY, CHECK, UNIQUE, NOT NULL и транзакции."),
        ("Потеря данных", "Online backup, integrity_check и persistent volume для production."),
        ("Потерянное обновление", "Поле version и ответ 409 при устаревшей версии."),
    ), widths=(5.0, 11.5), font_size=8.8)


def add_conclusion(doc: Document, spec: ReportSpec) -> None:
    doc.add_heading("7. Вывод по практике", level=1)
    add_para(doc, f"В ходе производственной практики по {spec.code} создан законченный учебный веб-проект FlowBoard. От исходной идеи канбан-доски выполнен переход к формализованным требованиям, модульной архитектуре, контракту API, реляционной схеме и работающему пользовательскому интерфейсу. Репозиторий содержит не только исходный код, но и инструкции запуска, OpenAPI, диаграммы, тест-план, материалы демонстрации и конфигурацию развертывания. Поэтому результат можно воспроизвести локально и проверить без скрытых зависимостей.", justify=False)
    if spec.code == "ПМ.02":
        add_para(doc, "Главной технической задачей стала надежная интеграция компонентов. Frontend передает данные только через JSON API, HTTP-слой выполняет проверки протокола и безопасности, сервисный слой применяет бизнес-правила, а database-модуль управляет транзакциями. Для каждого стыка определен контракт и способ обработки ошибки. Такой подход помог локализовать отладку: некорректный ввод проверяется на уровне сервиса, протокольные ошибки превращаются в понятный HTTP-ответ, а целостность данных обеспечивается SQL-ограничениями.", justify=False)
        add_para(doc, "Практика позволила закрепить разработку тестовых наборов. Тесты охватывают хеширование и проверку пароля, подпись и срок сессии, регистрацию, CRUD задач, конфликт версий, изоляцию пользователей и HTTP-сценарии. Отдельно проверены компиляция модулей, integrity_check базы и основной путь в браузере. Автоматический запуск в GitHub Actions делает проверку повторяемой при последующих изменениях.", justify=False)
        add_para(doc, "Сложность вызвали согласование drag-and-drop с доступными кнопками перемещения и предотвращение незаметной перезаписи одновременных изменений. Решением стали единый метод обновления карточки и поле version. Инспектирование кода привело к разделению ответственности, единообразному именованию, отсутствию runtime-зависимостей и выносу секретов в переменные окружения.", justify=False)
    else:
        add_para(doc, "Основной результат по работе с данными — нормализованная схема users, tasks, activities и schema_migrations. Внешние ключи задают владение и правила удаления, CHECK-ограничения не допускают недопустимых статусов и приоритетов, а индексы соответствуют реальным запросам интерфейса. Изменение карточки и запись аудита фиксируются атомарно. Поле version реализует optimistic locking и обнаруживает конкурентное обновление.", justify=False)
        add_para(doc, "Для администрирования разработана отдельная CLI-утилита. Она применяет миграции, выполняет контроль целостности, показывает статистику, создает согласованный backup и восстанавливает проверенную копию только после явного подтверждения. Защита построена в несколько слоев: scrypt для паролей, HMAC для сессии, CSRF для изменяющих запросов, параметризованный SQL, user_id в запросах и security headers HTTP.", justify=False)
        add_para(doc, "Наиболее важным было совместить удобство SQLite с требованиями к надежности. WAL улучшает одновременное чтение, транзакции обеспечивают атомарность, но для постоянного публичного развертывания файловой БД нужен persistent disk и один экземпляр приложения. Ограничение явно зафиксировано в документации; при росте нагрузки логичным продолжением станет миграция на PostgreSQL.", justify=False)
    add_para(doc, "Дальнейшее развитие проекта: совместные доски и роли участников, уведомления о сроках, экспорт, пагинация журнала, e2e-тесты и развернутый production-мониторинг. Code Climate можно подключить после регистрации открытого репозитория во внешнем сервисе, а публичный экземпляр — создать по готовому Render Blueprint. Эти шаги не меняют завершенность реализованной учебной версии, но повысят эксплуатационную зрелость проекта.", justify=False)
    add_para(doc, "Практика укрепила навыки анализа требований, проектирования интерфейсов и данных, безопасной разработки, тестирования, документирования и работы с Git. Полученный результат соответствует поставленной цели и может использоваться как основа для дальнейшего расширения.", justify=False)
    doc.add_paragraph()
    add_para(doc, "Подпись обучающегося: ____________________    Дата: «___» __________ 2026 г.", indent=False)


def add_appendix(doc: Document) -> None:
    doc.add_heading("Приложение А. Проверка и воспроизведение", level=1)
    add_para(doc, "Минимальные команды проверки:", bold=True, indent=False)
    code = (
        "git clone https://github.com/crankoff/PP_09.02.07.git\n"
        "cd PP_09.02.07\n"
        "python3 -m unittest discover -v\n"
        "python3 app.py\n"
        "# открыть http://localhost:8000\n"
        "# demo@example.com / Demo123!"
    )
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1)
    p.paragraph_format.right_indent = Cm(1)
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(code)
    r.font.name = "Courier New"
    r.font.size = Pt(9)
    set_cell_shading_like_paragraph(p, "F2F2F2")
    add_para(doc, "Ожидаемый результат: 17 тестов завершаются со статусом OK; после запуска health endpoint возвращает status=ok, вход открывает доску с демо-карточками. Административная проверка выполняется командами python3 scripts/db_admin.py check и python3 scripts/db_admin.py stats.")
    add_labeled_link(doc, "Репозиторий", REPO, REPO)
    add_labeled_link(doc, "Демонстрация", DEMO, DEMO)
    add_labeled_link(doc, "Развертывание", DEPLOY, DEPLOY)


def set_cell_shading_like_paragraph(paragraph, fill: str) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    p_pr.append(shd)


def build_report(spec: ReportSpec) -> Path:
    doc = clean_template(spec.template)
    configure_styles(doc)
    add_title_page(doc, spec)
    add_assignment(doc, spec)
    add_diary(doc, spec)
    add_attestation(doc, spec)
    add_characteristic(doc, spec)
    add_report_cover(doc, spec)
    add_selected_project(doc, spec)
    add_technical_passport(doc)
    add_architecture(doc, spec)
    add_traceability(doc, spec)
    add_demo_and_quality(doc)
    if spec.code == "ПМ.11":
        add_pm11_database_details(doc)
    add_conclusion(doc, spec)
    add_appendix(doc)
    doc.core_properties.title = f"Отчет по производственной практике {spec.code}: FlowBoard"
    doc.core_properties.subject = spec.module
    doc.core_properties.author = "Обучающийся АНПОО «Хекслет колледж»"
    doc.core_properties.keywords = "производственная практика, FlowBoard, 09.02.07"
    REPORTS.mkdir(parents=True, exist_ok=True)
    output = REPORTS / spec.filename
    doc.save(output)
    return output


def main() -> None:
    for spec in (PM02, PM11):
        output = build_report(spec)
        print(output)


if __name__ == "__main__":
    main()
