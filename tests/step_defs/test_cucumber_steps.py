from pytest_bdd import scenarios, parsers, given, when, then
from functools import partial
from cucumbers import CucumberBasket


scenarios('../features/cucumbers.feature')

CONVERTERS = {
    'initial': int,
    'some': int,
    'total': int,
}

EXTRA_TYPES = {
    'Number': int,
}

parse_num=partial(parsers.cfparse, extra_types=EXTRA_TYPES)

@given(
    parse_num('the basket has "{initial:Number}" cucumbers'), target_fixture='basket',
    converters=CONVERTERS)
def basket(initial):
    return CucumberBasket(initial_count=initial)


@when(parse_num('"{some:Number}" cucumbers are added to the basket'),
      converters=CONVERTERS)
def add_cucumbers(basket, some):
    basket.add(some)


@then(parse_num('the basket contains "{total:Number}" cucumbers'),
      converters=CONVERTERS)
def basket_has_total(basket, total):
    assert basket.count == total


@when(parse_num('"{some:Number}" cucumbers are removed from the basket'),
      converters=CONVERTERS)
def remove_cucumbers(basket, some):
    basket.remove(some)