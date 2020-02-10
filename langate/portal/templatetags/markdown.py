from django import template
from django.utils.safestring import mark_safe
from markdown import Markdown

register = template.Library()


@register.filter()
def markdown(markdown_body):
    return mark_safe(Markdown().convert(markdown_body))
