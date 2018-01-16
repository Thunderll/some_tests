# -*- coding:utf-8 -*-
from template_engine.templite import Templite
from collections import namedtuple


template_text = """
<p>Welcome, {{user_name}}!</p>
<p>Products:</p>
<ul>
{% for product in product_list %}
    <li>{{ product.name }}:
        {{ product.price|format_price}}</li>
{% endfor %}
</ul>
"""

Product = namedtuple('Product', ['name', 'price'])
product_list = [Product('Apple', 1), Product('Fig', 1.5), Product('Pomegranate', 3.25)]

def format_price(price):
    return '${0:.2f}'.format(price)


t = Templite(template_text, {'user_name': 'Charlite', 'product_list': product_list}, {'format_price': format_price})

print(t.render())