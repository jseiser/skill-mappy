from opsdroid.skill import Skill
from opsdroid.matchers import match_regex

# import aiohttp


class MappySkill(Skill):
    async def _get_deployments(self):
        sites = self.config["sites"]
        return_text = f"*Mappy Deployments*\n"
        for site in sites:
            return_text = f"{return_text}```Deployment: {site} URL: {self.config['sites'][site]['url']}```\n"
        return return_text

    # Matching Functions

    @match_regex(r"^mappy list deployments$")
    async def list_inventory(self, message):
        deployments = await self._get_deployments()

        await message.respond(f"{deployments}")
