#!/usr/bin/env python3
"""Build report diagrams and the browser-demo GIF.

Requires Pillow. This script is used only for documentation assets and is not
needed to run FlowBoard.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
DIAGRAM_DIR = ROOT / "docs" / "diagrams"
DEMO_DIR = ROOT / "docs" / "demo"
INK = "#172621"
TEAL = "#0D766D"
TEAL_PALE = "#D9EFEA"
VIOLET = "#7767A8"
SAND = "#CC9447"
PAPER = "#F3F0E9"
WHITE = "#FFFDF8"
LINE = "#CBD3CE"
MUTED = "#60706B"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default(size=size)


def rounded_box(draw: ImageDraw.ImageDraw, box, fill=WHITE, outline=LINE, radius=24, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def centered(draw: ImageDraw.ImageDraw, box, text: str, text_font, fill=INK, spacing=8):
    left, top, right, bottom = box
    bounds = draw.multiline_textbbox((0, 0), text, font=text_font, spacing=spacing, align="center")
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    draw.multiline_text(
        ((left + right - width) / 2, (top + bottom - height) / 2),
        text,
        font=text_font,
        fill=fill,
        spacing=spacing,
        align="center",
    )


def arrow(draw: ImageDraw.ImageDraw, start, end, color=TEAL, width=5):
    draw.line([start, end], fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 > x1 else -1
        points = [(x2, y2), (x2 - 18 * direction, y2 - 10), (x2 - 18 * direction, y2 + 10)]
    else:
        direction = 1 if y2 > y1 else -1
        points = [(x2, y2), (x2 - 10, y2 - 18 * direction), (x2 + 10, y2 - 18 * direction)]
    draw.polygon(points, fill=color)


def canvas(title: str, subtitle: str):
    image = Image.new("RGB", (1600, 900), PAPER)
    draw = ImageDraw.Draw(image)
    draw.text((80, 54), title, font=font(48, True), fill=INK)
    draw.text((82, 118), subtitle, font=font(22), fill=MUTED)
    draw.text((80, 842), "FlowBoard  ·  производственная практика 09.02.07", font=font(18, True), fill=TEAL)
    return image, draw


def build_architecture():
    image, draw = canvas("Архитектура приложения", "Один origin, модульный backend и транзакционная SQLite")
    boxes = [
        ((80, 270, 370, 490), "БРАУЗЕР", "HTML · CSS · JS\nFetch API · Drag & Drop"),
        ((455, 270, 745, 490), "HTTP СЛОЙ", "Маршруты · JSON\nCookie · CSRF · Headers"),
        ((830, 270, 1120, 490), "СЕРВИСЫ", "Валидация · права\nТранзакции · аудит"),
        ((1205, 270, 1495, 490), "SQLITE", "Users · Tasks\nActivities · Migrations"),
    ]
    for index, (box, heading, copy) in enumerate(boxes):
        rounded_box(draw, box, fill=WHITE, outline=TEAL if index in {1, 2} else LINE)
        draw.text((box[0] + 28, box[1] + 30), heading, font=font(22, True), fill=TEAL if index in {1, 2} else INK)
        draw.multiline_text((box[0] + 28, box[1] + 92), copy, font=font(22), fill=MUTED, spacing=12)
        if index < len(boxes) - 1:
            arrow(draw, (box[2] + 12, 380), (boxes[index + 1][0][0] - 12, 380))
    rounded_box(draw, (455, 585, 1120, 745), fill=TEAL_PALE, outline=TEAL)
    centered(draw, (455, 585, 1120, 745), "КОНТУР БЕЗОПАСНОСТИ\nscrypt · HMAC-SHA256 · rate limit · CSP · user_id isolation", font(21, True), fill=TEAL)
    arrow(draw, (600, 585), (600, 510), color=VIOLET)
    arrow(draw, (975, 585), (975, 510), color=VIOLET)
    rounded_box(draw, (1205, 585, 1495, 745), fill=WHITE)
    centered(draw, (1205, 585, 1495, 745), "DB ADMIN CLI\nmigrate · check\nbackup · restore", font(22, True))
    arrow(draw, (1350, 585), (1350, 510), color=SAND)
    image.save(DIAGRAM_DIR / "architecture.png")


def draw_table(draw, box, title, rows, accent):
    left, top, right, bottom = box
    rounded_box(draw, box, fill=WHITE, outline=accent, radius=18, width=3)
    draw.rounded_rectangle((left, top, right, top + 70), radius=18, fill=accent)
    draw.rectangle((left, top + 45, right, top + 70), fill=accent)
    draw.text((left + 24, top + 18), title, font=font(24, True), fill="white")
    y = top + 88
    for name, value in rows:
        draw.text((left + 22, y), name, font=font(18, True), fill=INK)
        draw.text((left + 175, y), value, font=font(18), fill=MUTED)
        y += 42


def build_erd():
    image, draw = canvas("ERD и модель данных", "Нормализованная схема, внешние ключи и аудит изменений")
    users = (90, 260, 500, 650)
    tasks = (600, 205, 1050, 710)
    activities = (1150, 260, 1510, 650)
    draw_table(draw, users, "USERS", [("PK", "id"), ("UK", "email"), ("", "password_hash"), ("", "display_name"), ("", "role"), ("", "created_at")], TEAL)
    draw_table(draw, tasks, "TASKS", [("PK", "id"), ("FK", "user_id"), ("", "title / description"), ("", "status / priority"), ("", "due_date / position"), ("", "version"), ("", "created_at / updated_at")], VIOLET)
    draw_table(draw, activities, "ACTIVITIES", [("PK", "id"), ("FK", "user_id"), ("FK", "task_id"), ("", "action"), ("", "details"), ("", "created_at")], SAND)
    arrow(draw, (515, 420), (585, 420), color=TEAL)
    draw.text((515, 380), "1", font=font(22, True), fill=TEAL)
    draw.text((565, 380), "N", font=font(22, True), fill=TEAL)
    arrow(draw, (1080, 420), (1135, 420), color=SAND)
    draw.text((1080, 380), "1", font=font(22, True), fill=SAND)
    draw.text((1120, 380), "N", font=font(22, True), fill=SAND)
    draw.line([(295, 665), (295, 750), (1330, 750), (1330, 665)], fill=TEAL, width=4)
    draw.text((790, 765), "USERS 1  ──  N ACTIVITIES", font=font(20, True), fill=TEAL, anchor="mm")
    image.save(DIAGRAM_DIR / "erd.png")


def actor(draw, x, y, label):
    draw.ellipse((x - 28, y - 70, x + 28, y - 14), outline=INK, width=5)
    draw.line((x, y - 14, x, y + 75), fill=INK, width=5)
    draw.line((x - 52, y + 12, x + 52, y + 12), fill=INK, width=5)
    draw.line((x, y + 75, x - 45, y + 132), fill=INK, width=5)
    draw.line((x, y + 75, x + 45, y + 132), fill=INK, width=5)
    centered(draw, (x - 120, y + 145, x + 120, y + 205), label, font(21, True))


def use_case(draw, center, text, accent=TEAL):
    x, y = center
    box = (x - 245, y - 52, x + 245, y + 52)
    draw.ellipse(box, fill=WHITE, outline=accent, width=4)
    centered(draw, box, text, font(21, True), fill=INK)
    return box


def build_use_case():
    image, draw = canvas("Сценарии использования", "Границы системы и два типа участников")
    draw.rounded_rectangle((370, 175, 1375, 805), radius=30, outline=LINE, width=4)
    draw.text((400, 195), "FLOWBOARD", font=font(20, True), fill=MUTED)
    actor(draw, 190, 400, "Пользователь")
    actor(draw, 1490, 500, "Администратор БД")
    user_cases = [
        use_case(draw, (680, 300), "Войти или\nзарегистрироваться"),
        use_case(draw, (680, 470), "Создать и\nизменить задачу"),
        use_case(draw, (680, 640), "Переместить задачу\nпо этапам"),
        use_case(draw, (1080, 385), "Найти и\nотфильтровать"),
        use_case(draw, (1080, 560), "Смотреть статистику\nи журнал"),
    ]
    for box in user_cases:
        draw.line((245, 410, box[0], (box[1] + box[3]) / 2), fill=TEAL, width=3)
    admin_cases = [
        use_case(draw, (1080, 700), "Миграции и\nпроверка БД", SAND),
        use_case(draw, (1080, 250), "Backup и restore", SAND),
    ]
    for box in admin_cases:
        draw.line((1435, 510, box[2], (box[1] + box[3]) / 2), fill=SAND, width=3)
    image.save(DIAGRAM_DIR / "use-case.png")


def build_demo():
    sources = [
        (DEMO_DIR / "frame-1-plan.png", "1. Задача запланирована"),
        (DEMO_DIR / "frame-2-edit.png", "2. Карточку можно изменить"),
        (DEMO_DIR / "frame-3-progress.png", "3. Задача перемещена в работу"),
    ]
    frames = []
    for path, caption in sources:
        source = Image.open(path).convert("RGB")
        # The in-app browser captures at a 2x backing scale. Keep the rendered quadrant.
        cropped = source.crop((0, 0, source.width // 2, source.height // 2))
        cropped = cropped.resize((1280, 884), Image.Resampling.LANCZOS)
        if not frames:
            cropped.save(DEMO_DIR / "flowboard-report.png", optimize=True)
        frame = Image.new("RGB", (1280, 956), INK)
        frame.paste(cropped, (0, 72))
        draw = ImageDraw.Draw(frame)
        draw.text((32, 19), caption, font=font(30, True), fill="white")
        draw.text((1238, 24), "FLOWBOARD", font=font(19, True), fill="#A9D6CC", anchor="ra")
        frames.append(frame.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
    frames[0].save(
        DEMO_DIR / "flowboard-demo.gif",
        save_all=True,
        append_images=frames[1:],
        duration=[2200, 2200, 3200],
        loop=0,
        optimize=True,
        disposal=2,
    )


def main():
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    build_architecture()
    build_erd()
    build_use_case()
    build_demo()
    print("Documentation assets built")


if __name__ == "__main__":
    main()
