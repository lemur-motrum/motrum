from django import template
from apps.core.models import SeoMetaTags
from urllib.parse import urlparse, parse_qs

register = template.Library()

@register.simple_tag(takes_context=True)
def get_seo_meta(context):
    request = context.get('request')
    url_name = None
    if hasattr(request, 'resolver_match'):
        url_name = request.resolver_match.url_name
    path = request.path if hasattr(request, 'path') else None
    full_path = request.get_full_path() if hasattr(request, 'get_full_path') else None

    def split_path_params(url):
        parsed = urlparse(url)
        norm_path = parsed.path.strip('/')
        params = {k: v[0] for k, v in parse_qs(parsed.query, keep_blank_values=True).items()}
        return norm_path, params

    meta = None
    # 1. Совпадение path и всех параметров из SeoMetaTags (в URL может быть больше параметров)
    if full_path:
        req_path, req_params = split_path_params(full_path)
        candidates = []
        for m in SeoMetaTags.objects.all():
            m_path, m_params = split_path_params(m.page)
            if m_path == req_path:
                # Все параметры из m_params должны быть в req_params с теми же значениями
                if all(k in req_params and req_params[k] == v for k, v in m_params.items()):
                    candidates.append(m)
        if candidates:
            # Берём наиболее специфичный (с наибольшим количеством параметров)
            meta = max(candidates, key=lambda m: len(split_path_params(m.page)[1]))
    # 2. Только path (без параметров)
    if not meta and path:
        norm_path = path.strip('/')
        meta = SeoMetaTags.objects.filter(page=norm_path).first()
    # 3. url_name
    if not meta and url_name:
        meta = SeoMetaTags.objects.filter(page=url_name).first()
    # 4. Без ведущего слэша (на всякий случай)
    if not meta and full_path and full_path.startswith('/'):
        meta = SeoMetaTags.objects.filter(page=full_path[1:]).first()
    if not meta and path and path.startswith('/'):
        meta = SeoMetaTags.objects.filter(page=path[1:]).first()
    if meta:
        return {
            'meta_title': meta.title,
            'meta_description': meta.description,
            'meta_h1': meta.h1,
        }
    return None 