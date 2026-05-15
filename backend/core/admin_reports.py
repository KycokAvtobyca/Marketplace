import html
import io
import os
from datetime import datetime
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.http import HttpResponse

from catalog.models import Brand, Category, ProductType
from orders.models import Order, OrderItem
from users.models import Shop


LOCAL_REPORT_APPS = {
    "users",
    "catalog",
    "marketing",
    "carts",
    "orders",
    "favorites",
    "reviews",
    "common",
}


def _money(value):
    value = value or Decimal("0.00")
    return f"{value:,.2f}".replace(",", " ") + " руб."


def _parse_report_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def _register_pdf_font():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont("MarketplaceSans", path))
            return "MarketplaceSans"
    return "Helvetica"


def _pdf_response(title, sections, filename, meta_rows=None, kpis=None):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    font_name = _register_pdf_font()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=22,
        leftMargin=22,
        topMargin=22,
        bottomMargin=22,
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName=font_name,
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1F2937"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName=font_name,
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#3B0764"),
            spaceBefore=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Cell",
            parent=styles["BodyText"],
            fontName=font_name,
            fontSize=7.5,
            leading=9.5,
        )
    )

    story = [Paragraph(title, styles["ReportTitle"]), Spacer(1, 8)]

    if meta_rows:
        meta_table = Table(meta_rows, colWidths=[95, 230, 95, 230])
        meta_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#334155")),
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E2E8F0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.extend([meta_table, Spacer(1, 10)])

    if kpis:
        kpi_table = Table([kpis], colWidths=[185] * len(kpis))
        kpi_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F3FF")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2E1065")),
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDD6FE")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDD6FE")),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.extend([kpi_table, Spacer(1, 10)])

    for section in sections:
        story.append(Paragraph(section["title"], styles["SectionTitle"]))
        table_data = [
            [Paragraph(str(cell), styles["Cell"]) for cell in row]
            for row in [section["headers"], *section["rows"]]
        ]
        table = Table(table_data, repeatRows=1, colWidths=section.get("col_widths"))
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4C1D95")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.extend([table, Spacer(1, 10)])

    doc.build(story)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _word_response(title, sections, filename, meta_rows=None, kpis=None):
    meta_html = ""
    if meta_rows:
        meta_html = "<table class='meta'>" + "".join(
            "<tr>" + "".join(f"<td>{html.escape(str(cell))}</td>" for cell in row) + "</tr>"
            for row in meta_rows
        ) + "</table>"

    kpi_html = ""
    if kpis:
        kpi_html = "<div class='kpis'>" + "".join(
            f"<div class='kpi'>{html.escape(str(kpi))}</div>" for kpi in kpis
        ) + "</div>"

    sections_html = ""
    for section in sections:
        rows_html = "".join(
            "<tr>" + "".join(f"<td>{html.escape(str(cell))}</td>" for cell in row) + "</tr>"
            for row in section["rows"]
        )
        headers_html = "".join(
            f"<th>{html.escape(str(cell))}</th>" for cell in section["headers"]
        )
        sections_html += f"""
          <h2>{html.escape(section["title"])}</h2>
          <table>
            <thead><tr>{headers_html}</tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
        """

    content = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <style>
          body {{ font-family: Arial, sans-serif; color: #1f2937; }}
          h1 {{ color: #2e1065; margin-bottom: 8px; }}
          h2 {{ color: #4c1d95; margin-top: 24px; }}
          table {{ border-collapse: collapse; width: 100%; margin-top: 8px; }}
          th {{ background: #4c1d95; color: white; text-align: left; }}
          th, td {{ border: 1px solid #cbd5e1; padding: 7px; font-size: 10pt; }}
          tr:nth-child(even) td {{ background: #f8fafc; }}
          .meta td:nth-child(odd) {{ font-weight: bold; background: #f1f5f9; }}
          .kpis {{ display: table; width: 100%; border-spacing: 8px; margin: 12px 0; }}
          .kpi {{ display: table-cell; background: #f5f3ff; border: 1px solid #ddd6fe; color: #2e1065; padding: 12px; text-align: center; font-weight: bold; }}
        </style>
      </head>
      <body>
        <h1>{html.escape(title)}</h1>
        {meta_html}
        {kpi_html}
        {sections_html}
      </body>
    </html>
    """
    response = HttpResponse(content, content_type="application/msword")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def _admin_form(title, body):
    return HttpResponse(
        f"""
        <!doctype html>
        <html lang="ru">
          <head>
            <meta charset="utf-8">
            <title>{html.escape(title)}</title>
            <style>
              body {{ font-family: Arial, sans-serif; margin: 0; color: #1f2937; background: #f8fafc; }}
              main {{ max-width: 920px; margin: 32px auto; background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 28px; box-shadow: 0 16px 40px rgba(15,23,42,.08); }}
              form {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }}
              label {{ display: grid; gap: 6px; font-weight: 700; font-size: 13px; }}
              input, select {{ padding: 11px; border: 1px solid #cbd5e1; border-radius: 10px; }}
              button, a.button {{ padding: 12px 16px; background: #4c1d95; color: white; border: 0; border-radius: 10px; text-decoration: none; cursor: pointer; font-weight: 700; }}
              .row {{ display: flex; gap: 12px; align-items: center; }}
              .wide {{ grid-column: 1 / -1; }}
            </style>
          </head>
          <body>
            <main>
              <p><a href="/admin/">← Админ-панель</a></p>
              <h1>{html.escape(title)}</h1>
              {body}
            </main>
          </body>
        </html>
        """
    )


def _option_list(items, selected=""):
    return "".join(
        f'<option value="{obj.pk}" {"selected" if str(obj.pk) == str(selected) else ""}>{html.escape(obj.name)}</option>'
        for obj in items
    )


def _shop_report_filter_options(shop):
    product_qs = shop.products.all()
    return {
        "categories": Category.objects.filter(product__in=product_qs).distinct().order_by("name"),
        "product_types": ProductType.objects.filter(products__in=product_qs).distinct().order_by("name"),
        "brands": Brand.objects.filter(products__in=product_qs).distinct().order_by("name"),
    }


def _shop_report_context(request):
    shops = Shop.objects.all().order_by("name")
    if request.user.is_superuser:
        shop_id = request.GET.get("shop")
        shop = shops.filter(pk=shop_id).first() if shop_id else shops.first()
    else:
        shop = request.user.shop.first()

    if not shop:
        raise PermissionDenied("У пользователя нет магазина для отчета.")

    return {
        "shops": shops,
        "shop": shop,
        "category_id": request.GET.get("category"),
        "product_type_id": request.GET.get("product_type"),
        "brand_id": request.GET.get("brand"),
        "status_value": request.GET.get("status"),
        "sort_value": request.GET.get("sort") or "product",
    }


def _build_shop_report(request, context):
    shop = context["shop"]
    status_value = context["status_value"]
    qs = (
        OrderItem.objects.select_related(
            "order",
            "product_variant",
            "product_variant__product",
            "product_variant__product__category",
            "product_variant__product__product_type",
            "product_variant__product__brand",
        )
        .filter(product_variant__product__shop=shop)
    )

    if status_value:
        qs = qs.filter(order__status=status_value)
    else:
        qs = qs.exclude(order__status=Order.Status.CANCELED)

    date_from = date_to = None
    if not request.GET.get("all_time"):
        date_from = _parse_report_date(request.GET.get("date_from") or request.GET.get("date"))
        date_to = _parse_report_date(request.GET.get("date_to"))
        if date_from:
            qs = qs.filter(order__date_time_create__date__gte=date_from)
        if date_to:
            qs = qs.filter(order__date_time_create__date__lte=date_to)

    if context["category_id"]:
        qs = qs.filter(product_variant__product__category_id=context["category_id"])
    if context["product_type_id"]:
        qs = qs.filter(product_variant__product__product_type_id=context["product_type_id"])
    if context["brand_id"]:
        qs = qs.filter(product_variant__product__brand_id=context["brand_id"])

    revenue_expr = ExpressionWrapper(
        F("quantity") * F("discounted_price_per_item"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    annotated = qs.annotate(line_revenue=revenue_expr)
    totals = annotated.aggregate(
        revenue=Sum("line_revenue"),
        quantity=Sum("quantity"),
        order_count=Count("order", distinct=True),
    )

    summary = (
        annotated.values(
            "product_variant__product__name",
            "product_variant__product__category__name",
            "product_variant__product__product_type__name",
            "product_variant__product__views",
            "product_variant__sku",
        )
        .annotate(quantity=Sum("quantity"), revenue=Sum("line_revenue"))
    )
    sort_map = {
        "revenue": ("-revenue", "product_variant__product__name"),
        "quantity": ("-quantity", "product_variant__product__name"),
        "views": ("-product_variant__product__views", "product_variant__product__name"),
        "product": ("product_variant__product__name", "product_variant__sku"),
    }
    summary = summary.order_by(*sort_map.get(context["sort_value"], sort_map["product"]))

    product_rows = []
    for row in summary:
        product_rows.append(
            [
                row["product_variant__product__name"],
                row["product_variant__sku"],
                row["product_variant__product__category__name"] or "-",
                row["product_variant__product__product_type__name"] or "-",
                row["product_variant__product__views"] or 0,
                row["quantity"] or 0,
                _money(row["revenue"]),
            ]
        )

    order_rows = []
    for item in annotated.order_by("-order__date_time_create", "-order_id", "product_variant__sku"):
        order_rows.append(
            [
                f"#{item.order_id}",
                item.order.date_time_create.strftime("%d.%m.%Y %H:%M"),
                item.order.get_status_display(),
                item.product_variant.product.name,
                item.product_variant.sku,
                item.quantity,
                _money(item.line_revenue),
            ]
        )

    if not product_rows:
        product_rows.append(["Нет данных", "", "", "", "", "", ""])
    if not order_rows:
        order_rows.append(["Нет данных", "", "", "", "", "", ""])

    period = "за все время" if request.GET.get("all_time") else "выбранный период"
    if date_from or date_to:
        period = f"{date_from or '...'} - {date_to or '...'}"

    meta_rows = [
        ["Магазин", shop.name, "Период", period],
        ["Статус", dict(Order.Status.choices).get(status_value, "Все кроме отмененных"), "Сформировано", datetime.now().strftime("%d.%m.%Y %H:%M")],
    ]
    kpis = [
        f"Заказов: {totals['order_count'] or 0}",
        f"Продано: {totals['quantity'] or 0} шт.",
        f"Выручка: {_money(totals['revenue'])}",
    ]
    sections = [
        {
            "title": "Сводка по товарам",
            "headers": ["Товар", "SKU", "Категория", "Тип", "Просмотры", "Кол-во", "Выручка"],
            "rows": product_rows,
            "col_widths": [170, 70, 110, 110, 60, 55, 85],
        },
        {
            "title": "Оформленные заказы",
            "headers": ["Заказ", "Дата", "Статус", "Товар", "SKU", "Кол-во", "Сумма"],
            "rows": order_rows,
            "col_widths": [45, 80, 115, 175, 70, 55, 85],
        },
    ]
    return meta_rows, kpis, sections


def shop_report_view(request):
    if not request.user.is_staff:
        raise PermissionDenied

    context = _shop_report_context(request)
    shop = context["shop"]

    if "download" not in request.GET:
        filter_options = _shop_report_filter_options(shop)
        shop_options = "".join(
            f'<option value="{shop_obj.pk}" {"selected" if shop_obj.pk == shop.pk else ""}>{html.escape(shop_obj.name)}</option>'
            for shop_obj in context["shops"]
        )
        status_options = "".join(
            f'<option value="{value}" {"selected" if value == context["status_value"] else ""}>{html.escape(label)}</option>'
            for value, label in Order.Status.choices
        )
        sort_options = "".join(
            f'<option value="{value}" {"selected" if value == context["sort_value"] else ""}>{label}</option>'
            for value, label in [
                ("product", "По товару"),
                ("revenue", "По выручке"),
                ("quantity", "По количеству"),
                ("views", "По просмотрам"),
            ]
        )
        shop_select = (
            f"<label>Магазин<select name='shop'>{shop_options}</select></label>"
            if request.user.is_superuser
            else ""
        )
        return _admin_form(
            "Отчет магазина",
            f"""
            <form method="get">
              {shop_select}
              <label>Дата с<input type="date" name="date_from" value="{html.escape(request.GET.get("date_from", ""))}"></label>
              <label>Дата по<input type="date" name="date_to" value="{html.escape(request.GET.get("date_to", ""))}"></label>
              <label class="row wide"><input type="checkbox" name="all_time" value="1"> За все время</label>
              <label>Категория<select name="category"><option value="">Все</option>{_option_list(filter_options["categories"], context["category_id"])}</select></label>
              <label>Тип продукта<select name="product_type"><option value="">Все</option>{_option_list(filter_options["product_types"], context["product_type_id"])}</select></label>
              <label>Бренд<select name="brand"><option value="">Все</option>{_option_list(filter_options["brands"], context["brand_id"])}</select></label>
              <label>Статус заказа<select name="status"><option value="">Все кроме отмененных</option>{status_options}</select></label>
              <label>Сортировка<select name="sort">{sort_options}</select></label>
              <div class="row wide">
                <button type="submit" name="download" value="1">Скачать PDF</button>
                <button type="submit" name="download" value="word">Скачать Word</button>
              </div>
            </form>
            """,
        )

    meta_rows, kpis, sections = _build_shop_report(request, context)
    title = f"Отчет магазина {shop.name}"
    if request.GET.get("download") == "word":
        return _word_response(title, sections, f"shop-report-{shop.pk}.doc", meta_rows, kpis)
    return _pdf_response(title, sections, f"shop-report-{shop.pk}.pdf", meta_rows, kpis)


def _date_field_name(model):
    preferred = ["date_time_create", "created_at", "data_time_create", "date_joined"]
    field_names = {field.name for field in model._meta.fields}
    for name in preferred:
        if name in field_names:
            return name
    for field in model._meta.fields:
        if isinstance(field, (models.DateField, models.DateTimeField)):
            return field.name
    return None


def _date_filter_kwargs(model, field_name, report_date):
    field = model._meta.get_field(field_name)
    if isinstance(field, models.DateTimeField):
        return {f"{field_name}__date": report_date}
    return {field_name: report_date}


def table_report_view(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    content_types = ContentType.objects.filter(app_label__in=LOCAL_REPORT_APPS).order_by(
        "app_label", "model"
    )

    if "download" not in request.GET:
        options = "".join(
            f'<option value="{ct.pk}">{html.escape(ct.app_label)}.{html.escape(ct.model)}</option>'
            for ct in content_types
        )
        return _admin_form(
            "Отчет по таблице БД",
            f"""
            <form method="get">
              <label class="wide">Таблица<select name="content_type">{options}</select></label>
              <label>Дата отчета<input type="date" name="date"></label>
              <label class="row"><input type="checkbox" name="all_time" value="1"> За все время</label>
              <div class="row wide">
                <button type="submit" name="download" value="1">Скачать PDF</button>
                <button type="submit" name="download" value="word">Скачать Word</button>
              </div>
            </form>
            """,
        )

    ct = content_types.filter(pk=request.GET.get("content_type")).first()
    if not ct:
        raise PermissionDenied("Недоступная таблица.")

    model = ct.model_class()
    date_field = _date_field_name(model)
    report_date = None if request.GET.get("all_time") else _parse_report_date(request.GET.get("date"))

    qs = model.objects.all()
    if report_date and date_field:
        qs = qs.filter(**_date_filter_kwargs(model, date_field, report_date))
    qs = qs.order_by("-pk") if model._meta.pk else qs

    fields = [
        field
        for field in model._meta.fields
        if not isinstance(field, models.BinaryField)
    ][:8]
    rows = [[str(getattr(obj, field.name, ""))[:120] for field in fields] for obj in qs[:300]]
    if not rows:
        rows = [["Нет данных"] + [""] * (len(fields) - 1)]

    period = report_date.strftime("%d.%m.%Y") if report_date else "за все время"
    title = f"Отчет по таблице {ct.app_label}.{ct.model}: {period}"
    sections = [
        {
            "title": "Данные таблицы",
            "headers": [field.verbose_name or field.name for field in fields],
            "rows": rows,
        }
    ]
    if request.GET.get("download") == "word":
        return _word_response(title, sections, f"table-report-{ct.app_label}-{ct.model}.doc")
    return _pdf_response(title, sections, f"table-report-{ct.app_label}-{ct.model}.pdf")
