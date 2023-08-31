.. tab-set::

   .. tab-item:: Score

      {% for line in content %}{{ line }}
      {% endfor %}

   .. tab-item:: Source

      .. code:: rst
       
         {% for line in content %}{{ line }}
         {% endfor %}
