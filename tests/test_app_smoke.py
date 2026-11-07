"""Headless UI smoke test: clicks through the whole app and fails on any exception.

Run before every pull request that touches app.py or ui/:   pytest -q -m ui
Takes about 30-60 seconds.
"""
import random

import pytest
from streamlit.testing.v1 import AppTest

pytestmark = pytest.mark.ui


def _no_errors(at):
    assert not at.exception, [e.value for e in at.exception]


@pytest.fixture(scope="module")
def at():
    app = AppTest.from_file("../app.py", default_timeout=240)
    app.run()
    _no_errors(app)
    return app


def _click(at, label):
    [b for b in at.button if b.label == label][0].click().run()
    _no_errors(at)


def test_presets_plan_reset(at):
    for label in ["Laid off, EI 55%, 6 mo", "Furnace: 1 mo spending", "Job loss + bills 15%",
                  "Write the plan for the customer", "Reset"]:
        _click(at, label)


def test_custom_twist_card(at):
    at.text_area(key="card_text").set_value("Rent goes up by $400 a month and the car needs a $2,500 repair.").run()
    _click(at, "Read card")
    assert at.session_state.spend_inc == 400 and at.session_state.one_off == 2500


def test_time_machine_and_demo_account(at):
    for label in ["Dec 2024", "Dec 2023", "Today (Dec 2025)"]:
        at.selectbox(key="asof_label").set_value(label).run()
        _no_errors(at)
    at.selectbox(key="asof_label").set_value("Dec 2024").run()
    at.number_input(key="acct").set_value(93172).run()
    _no_errors(at)
    assert any("riskiest 10%" in m.value for m in at.markdown)
    at.selectbox(key="asof_label").set_value("Today (Dec 2025)").run()


def test_tricky_accounts(at):
    for acct in [20176, 56072, 93172, 32179, 20111]:   # pensioner, 16-year-old owner, demo, overdrawn, no bills
        at.number_input(key="acct").set_value(acct).run()
        _no_errors(at)


def test_controls(at):
    _click(at, "Job loss + bills 15%")
    at.slider(key="emp_share").set_value(50).run(); _no_errors(at)
    at.radio(key="opt_outcome").set_value("a typical outcome (median)").run(); _no_errors(at)
    at.slider(key="opt_cap").set_value(100).run(); _no_errors(at)
    at.toggle(key="wl_early").set_value(False).run(); _no_errors(at)


def test_random_accounts(at):
    import engine as E
    accounts = sorted(E.load()["monthly"].account_id.unique().tolist())
    random.seed(7)
    for acct in random.sample(accounts, 15):
        at.number_input(key="acct").set_value(acct).run()
        _no_errors(at)
