from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

import aiohttp


class MappySkill(Skill):
    async def _get_deployments(self):
        sites = self.config["sites"]
        return_text = f"*Mappy Deployments*\n"
        for site in sites:
            return_text = f"{return_text}```Deployment: {site} URL: {self.config['sites'][site]['url']}```\n"
        return return_text

    async def _rest_call(self, deployment, api_url, call_method):
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            if call_method == "get":
                async with session.get(api_url) as resp:
                    data = await resp.json()
                    return data
            else:
                async with session.post(api_url) as resp:
                    data = await resp.json()
                    return data

    async def _list_groups(self, deployment):
        api_url = f"{self.config['sites'][deployment]['url']}/api/v1/groups"
        data = await self._rest_call(deployment, api_url, "get")
        return data["_items"]

    # Matching Functions

    @match_regex(r"^mappy list deployments$")
    async def list_inventory(self, message):
        deployments = await self._get_deployments()

        await message.respond(f"{deployments}")

    @match_regex(r"^mappy(?P<deployment>dev|prd|stage) list groups$")
    async def list_groups(self, message):
        deployment = message.regex.group("deployment")
        groups = await self._list_groups(deployment)

        await message.respond(f"{groups}")
