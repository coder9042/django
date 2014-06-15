from django import http
from django.http.response import REASON_PHRASES as MSG
from django.template import (Context, RequestContext,
                             loader, Template, TemplateDoesNotExist)
from django.views.decorators.csrf import requires_csrf_token


# This can be called when CsrfViewMiddleware.process_view has not run,
# therefore need @requires_csrf_token in case the template needs
# {% csrf_token %}.

@requires_csrf_token
def page_not_found(request, template_name='404.html'):
    """
    Default 404 handler.

    Templates: :template:`404.html`
    Context:
        request_path
            The path of the requested URL (e.g., '/app/pages/bad_page/')
    """
    try:
        template = loader.get_template(template_name)
        content_type = None             # Django will use DEFAULT_CONTENT_TYPE
    except TemplateDoesNotExist:
        template = Template(
            '<h1>Not Found</h1>'
            '<p>The requested URL {{ request_path }} was not found on this server.</p>')
        content_type = 'text/html'
    body = template.render(RequestContext(request, {'request_path': request.path}))
    return http.HttpResponseNotFound(body, content_type=content_type)


@requires_csrf_token
def server_error(request, view_type='500', message=''):
    """
    5xx error handler.
    """
    status = int(view_type)
    template_name = "%s.html" % view_type
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return http.HttpResponse('<h1>%s (%s)</h1><p>%s</p>' % (MSG[status], view_type, message), status=status, content_type='text/html')
    return http.HttpResponse(template.render(Context({})), status=status)


@requires_csrf_token
def client_error(request, view_type='400', message=''):
    """
    4xx error handler.
    """
    if view_type == '404':
        page_not_found(request)
    status = int(view_type)
    template_name = "%s.html" % view_type
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return http.HttpResponse('<h1>%s (%s)</h1><p>%s</p>' % (MSG[status], view_type, message), status=status, content_type='text/html')
    return http.HttpResponse(template.render(Context({})), status=status)
