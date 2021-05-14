from datetime import timedelta
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from app.core.light import get_light
from app.services.pi_light.color import Color
from app.services.pi_light.day import Day
from app.services.pi_light.light import Light
from app.services.pi_light.mode import Mode
from app.services.pi_light.rule import Rule
from app.services.pi_light.rule_manager import RuleDoesNotExistError
from app.services.pi_light.state import State

router = APIRouter()


@router.get(
    "/color",
    response_model=Color,
    summary="Get the current color",
    response_description="The current color",
)
def color(light: Light = Depends(get_light)) -> Color:
    return light.color


@router.get(
    "/state",
    response_model=State,
    summary="Get the current light state",
    response_description="The current state",
)
def state(light: Light = Depends(get_light)) -> State:
    return light.state()


@router.get(
    "/mode",
    response_model=Mode,
    summary="Get the current light mode",
    response_description="The current mode",
)
def mode(light: Light = Depends(get_light)) -> Mode:
    return light.mode()


@router.get(
    "/rules/current",
    summary="Get the current rule and percentage through the rule",
    response_description="The current rule and percentage through the rule",
)
def current_rule(light: Light = Depends(get_light)) -> Tuple[Optional[Rule], float]:
    return light.rule_manager.current_rule()


@router.get(
    "/rules/next",
    summary="Get the next rule and time until the next rule",
    response_description="The next rule and time until the next rule",
)
def next_rule(light: Light = Depends(get_light)) -> Tuple[Optional[Rule], timedelta]:
    return light.rule_manager.next_rule()


@router.get(
    "/rules",
    summary="Get the set of all rules",
    response_description="The set of all rules",
)
def rules(light: Light = Depends(get_light)) -> Dict[Day, List[Rule]]:
    return light.rule_manager.rules


@router.post(
    "/rules",
    summary="Add a new rule to the set of all rules",
    response_description="The updated set of all rules",
)
def add_rule(
    rule: Rule = Body(...), light: Light = Depends(get_light)
) -> Dict[Day, List[Rule]]:
    light.rule_manager.add_rule(rule)
    return light.rule_manager.rules


@router.delete(
    "/rules",
    summary="Remove a rule from the set of all rules",
    response_description="The updated set of all rules",
    responses={400: {}},
)
def remove_rule(
    rule: Rule = Body(...), light: Light = Depends(get_light)
) -> Dict[Day, List[Rule]]:
    try:
        light.rule_manager.remove_rule(rule)
    except RuleDoesNotExistError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Rule does not exist"
        )
    return light.rule_manager.rules
