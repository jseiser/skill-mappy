from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)


class MappySkill(Skill):
    async def _get_deployments(self):
        sites = self.config["sites"]
        return_text = f"*Mappy Deployments*\n"
        for site in sites:
            return_text = f"{return_text}```Deployment: {site} URL: {self.config['sites'][site]['url']}```\n"
        return return_text

    async def _rest_call(self, deployment, api_url, payload=None):
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            if payload:
                async with session.get(api_url, params=payload) as resp:
                    _LOGGER.info(resp.url)
                    data = await resp.json()
                    return data
            else:
                async with session.get(api_url) as resp:
                    data = await resp.json()
                    return data

    async def _list_groups(self, deployment):
        api_url = f"{self.config['sites'][deployment]['url']}/api/v1/groups"
        data = await self._rest_call(deployment, api_url)

        items = data["_items"]

        return_text = f"*Mappy {deployment}*\n"
        for i in items:
            return_text = f"{return_text}```Name: {i['name']} ID: {i['_id']}```\n"
        return return_text

    async def _get_group_name(self, deployment, name):
        api_url = f"{self.config['sites'][deployment]['url']}/api/v1/groups"
        lookup = f'{{"name": "{name}"}}'
        payload = {"where": lookup}
        _LOGGER.info(payload)
        data = await self._rest_call(deployment, api_url, payload)

        if "_items" in data:
            for i in data["_items"]:
                group_id = i["_id"]
                name = i["name"]
                hosts = i["hosts"]
                # group_vars = i["groupvars"]
            host_line = "\n".join(hosts)
            return_text = f"*Mappy {deployment}*\n```Name: {name}\nID: {group_id}```\n*Hosts*\n{host_line}"
            return return_text
        else:
            return_text = f"*Mappy {deployment}*\n"
            return_text = f"{return_text}```Group Not Found```\n"
            return return_text

    # Matching Functions

    @match_regex(r"^mappy list deployments$")
    async def list_inventory(self, message):
        deployments = await self._get_deployments()

        await message.respond(f"{deployments}")

    @match_regex(r"^mappy (?P<deployment>dev|prd|stage) list groups$")
    async def list_groups(self, message):
        deployment = message.regex.group("deployment")
        groups = await self._list_groups(deployment)

        await message.respond(f"{groups}")

    @match_regex(r"^mappy (?P<deployment>dev|prd|stage) get group name: (?P<name>.*)$")
    async def get_group_name(self, message):
        deployment = message.regex.group("deployment")
        name = message.regex.group("name")
        group = await self._get_group_name(deployment, name)

        await message.respond(f"{group}")
