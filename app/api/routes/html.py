from datetime import datetime, time, timedelta

import humanize
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from loguru import logger
from pydantic import ValidationError

from app.core.config import Settings
from app.core.light import get_light
from app.core.settings import get_settings
from app.services.pi_light.color import Color
from app.services.pi_light.day import Day
from app.services.pi_light.light import Light
from app.services.pi_light.mode import Mode
from app.services.pi_light.rule import Rule
from app.services.pi_light.rule_manager import RuleDoesNotExistError

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/favicon.ico")
async def favicon():
    return FileResponse("app/templates/favicon.ico")


@router.route("/", methods=["GET", "POST"])
async def light_form(request: Request):
    light = get_light()
    form_data = await request.form()
    if "add_rule" in form_data.keys():
        try:
            start_time = time_to_msec(
                datetime.strptime(form_data.get("start_time"), "%H:%M").time()
            )
            stop_time = time_to_msec(
                datetime.strptime(form_data.get("stop_time"), "%H:%M").time()
            )
            start_color = Color.from_hex(
                form_data.get("start_color"),
                brightness=int(form_data.get("start_color_brightness")) / 100.0,
            )
            stop_color = Color.from_hex(
                form_data.get("stop_color"),
                brightness=int(form_data.get("stop_color_brightness")) / 100.0,
            )
            light.rule_manager.add_rule(
                Rule(
                    day=Day(form_data.get("day")),
                    start_time=start_time,
                    stop_time=stop_time,
                    start_color=start_color,
                    stop_color=stop_color,
                )
            )
        except (ValidationError, ValueError) as e:
            logger.info(f"Issue parsing Add Rule form: {e}")
    elif "remove_rule" in form_data.keys():
        for rule_hash in form_data.getlist("rule_hashes"):
            try:
                light.rule_manager.remove_rule_by_hash(int(rule_hash))
            except RuleDoesNotExistError as e:
                logger.info(f"Issue removing rule: {rule_hash}, {e}")
    elif "set_mode" in form_data.keys():
        mode = Mode(form_data.get("mode"))
        light.set_mode(mode)
        if mode == Mode.DEFAULT:
            light.color = Color.from_hex(
                form_data.get("mode_color"),
                brightness=int(form_data.get("mode_color_brightness")) / 100.0,
            )
    return render_light_template(request, light)


def render_light_template(request, light: Light, settings: Settings = get_settings()):
    light_current_rule = light.rule_manager.current_rule()[0]
    current_rule_str = (
        light_current_rule.time_interval() if light_current_rule else "No Active Rule"
    )
    light_next_rule = light.rule_manager.next_rule()
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
            "current_time": datetime.now().strftime(settings.time_format),
            "mode": light.mode(),
            "current_rule_str": current_rule_str,
            "current_color": light.color,
            "next_rule": next_rule,
            "time_until_change": time_until_change,
            "rules": light.rule_manager.rules,
        },
    )


def time_to_msec(t: time) -> int:
    td = datetime.combine(datetime.min, t) - datetime.min
    return td // timedelta(milliseconds=1)
