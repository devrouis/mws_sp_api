

from django import template

register = template.Library()

def left(text, n):
  return text[:n]

@register.filter
def abstract(value):
  length = 10
  if not value or len(value) <= 10:
    return value
  return f'{left(value, length)}...'