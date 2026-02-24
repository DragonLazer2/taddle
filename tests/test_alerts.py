from taddle.alerts import AlertDispatcher
from taddle.events import Event, EventType, Severity


def _make_event(severity: Severity) -> Event:
    return Event(
        event_type=EventType.FILE_CREATED,
        severity=severity,
        source_monitor="test",
        path="/tmp/x",
        description="test event",
        event_id="test-id",
    )


def test_dispatch_all():
    dispatcher = AlertDispatcher()
    received = []
    dispatcher.register(lambda ev: received.append(ev))
    dispatcher.dispatch(_make_event(Severity.INFO))
    assert len(received) == 1


def test_dispatch_severity_filter():
    dispatcher = AlertDispatcher()
    received = []
    dispatcher.register(lambda ev: received.append(ev), severity=Severity.WARNING)
    dispatcher.dispatch(_make_event(Severity.INFO))
    assert len(received) == 0
    dispatcher.dispatch(_make_event(Severity.WARNING))
    assert len(received) == 1
    dispatcher.dispatch(_make_event(Severity.CRITICAL))
    assert len(received) == 2


def test_unregister():
    dispatcher = AlertDispatcher()
    received = []
    cb = lambda ev: received.append(ev)
    dispatcher.register(cb)
    dispatcher.dispatch(_make_event(Severity.INFO))
    assert len(received) == 1
    dispatcher.unregister(cb)
    dispatcher.dispatch(_make_event(Severity.INFO))
    assert len(received) == 1  # no new call


def test_bad_callback_does_not_crash():
    dispatcher = AlertDispatcher()

    def bad_cb(ev):
        raise RuntimeError("boom")

    received = []
    dispatcher.register(bad_cb)
    dispatcher.register(lambda ev: received.append(ev))
    dispatcher.dispatch(_make_event(Severity.INFO))
    # Second callback still received the event despite first raising
    assert len(received) == 1
