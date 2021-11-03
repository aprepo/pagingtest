from app.aiven import cache, headers
from app.settings import BASEURL


def get_projects(token):
    session = cache.get_private_session(token)
    response = session.get('https://api.aiven.io/v1/project', headers=headers.get_headers(token))
    if response:
        return_value = { 'from_cache': response.from_cache, 'projects': []}

        def _billing_group_url_or_none(account_id, group_id):
            if group_id is None or account_id is None:
                return None
            return f"{BASEURL}/accounts/{account_id}/billing_group/{group_id}"

        def _account_or_none(account_id, account_name):
            if account_id is None or account_name is None:
                return None
            else:
                return {
                    'account_id': account_id,
                    'account_name': account_name,
                    'url': f"{BASEURL}/accounts/{account_id}/",
                }

        for project in response.json().get("projects", []):
            return_value['projects'].append({
                'tenant_id': project.get('tenant_id', None),
                'project_name': project.get('project_name', None),
                'account': _account_or_none(
                    project.get('account_id', None), 
                    project.get('account_name', None)
                    ),
                'billing': {
                    'billing_group_id': project.get('billing_group_id', None),
                    'billing_group_name': project.get('billing_group_name', None),
                    "url": _billing_group_url_or_none(
                        project.get('account_id', None), 
                        project.get('billing_group_id')
                        )
                },
                'services': f"{BASEURL}/services?project={project.get('project_name')}"
            })
        return return_value, response.from_cache
    else:
        raise Exception(response.json())
