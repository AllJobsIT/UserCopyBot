import os

import aiohttp


class GraphQLClient:

    def _definition_variables(self, variables: dict):
        if variables:
            variables_types = ", ".join(f'${key}: String!' for key in variables.keys())
            variables = ", ".join(f"{key}: ${key}" for key in variables.keys())
        else:
            variables_types = None
            variables = None
        return variables, variables_types

    async def post_query(self, name_nutation: str, name_query: str, fields: list, variables: dict = None):
        mutation_variables, mutation_variables_types = self._definition_variables(variables)
        query = \
            f"""
            mutation {name_nutation} ({mutation_variables_types}) {{
                {name_query} ({mutation_variables}) {{
                    {' '.join(fields)}
                }}
            }}    
            """
        return query, name_query

    async def get_query(self, name_query: str, fields: list):
        query = \
            f"""
            {name_query} {{
                {' '.join(fields)}
            }}
            """
        return query, name_query

    async def execute(self, query, name_query: str = None, variables: dict = None):
        query = {'query': query}
        if variables:
            query.update({"variables": variables})
        async with aiohttp.ClientSession() as session:
            async with session.post(os.getenv("API_URL"), json=query) as resp:
                response = await resp.json()
                return response['data'][name_query]
