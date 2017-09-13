**tindo:**

A micro-framework based on wsgiref

# 1 Design RoadMap
**Main Components**

+ *get* decorator: for HTTP GET Method
+ *post* decorator: for HTTP POST Method
+ *Route* class: wrap the decorated functions, which contains the `match(self, url)` methods to determinate whether
the url match the route nor not.
+ *Request* class: wrap the wsgi's `environ` dictionary into more useful apis, including `methods`, `cookies`, `path`
 and `inputs` etc.
+ *Response* class: a high-level of wsgi's `status` and `response_headers`.
+ *view* decorator: a specific html template to render
+ *WSGIApplication* class: main class of web framework. To approach the multi-thread environment, use threading module'
s `Local` class.
