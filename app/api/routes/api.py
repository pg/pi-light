from fastapi import APIRouter, Depends, Body, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from app.core.light import get_light
from app.services.pi_light.days import Day
from app.services.pi_light.light import Light, RuleDoesNotExistError
from app.services.pi_light.rule import Rule

router = APIRouter()


@router.get('/color')
def color(light: Light = Depends(get_light)):
    return light.color()


@router.get('/rules')
def rules(light: Light = Depends(get_light)):
    return light.rules


@router.post("/rules")
def add_rule(
        rule: Rule = Body(...),
        day: Day = Body(...),
        light: Light = Depends(get_light)
):
    light.add_rule(rule, day)
    return light.rules


@router.delete("/rules", responses={400: {}})
def remove_rule(
        rule: Rule = Body(...),
        day: Day = Body(...),
        light: Light = Depends(get_light)
):
    try:
        light.remove_rule(rule, day)
    except RuleDoesNotExistError:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Rule does not exist"
        )
    return light.rules
