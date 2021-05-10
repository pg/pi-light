import humanize
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.core.light import get_light
from app.services.pi_light.day import Day
from app.services.pi_light.rule import Rule

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.route("/", methods=["GET", "POST"])
async def light_form(request: Request):
    light = get_light()
    form_data = await request.form()
    if "add" in form_data.keys():
        light.add_rule(Rule(), Day.SUNDAY)  # FIXME: Use starlette wtf forms here
    elif "remove" in form_data.keys():
        for rule_hash in form_data.getlist("rule_hashes"):
            light.remove_rule_by_hash(int(rule_hash))
    return render_light_template(request, light)


def render_light_template(request, light):
    current_rule_str = (
        light.current_rule()[0].time_interval()
        if light.current_rule()[0]
        else "No Active Rule"
    )
    current_color_hex = light.color().hex
    light_next_rule = light.next_rule()
    next_rule = (
        light_next_rule[0].time_interval()
        if light_next_rule[0]
        else "No more rules today"
    )
    time_until_change = humanize.naturaldelta(light_next_rule[1])
    return templates.TemplateResponse(
        "light.html",
        {
            "request": request,
            "current_rule_str": current_rule_str,
            "current_color_hex": current_color_hex,
            "next_rule": next_rule,
            "time_until_change": time_until_change,
            "rules": light.rules,
        },
    )
