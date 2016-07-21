from learning_journal.models import Entry, DBSession


def test_create_entry(dbtransaction):
    """Test for a change of state of the model."""
    new_model = Entry(title='something', text='something else')
    assert new_model.id is None
    DBSession.add(new_model)
    DBSession.flush()
    assert new_model.id is not None


def test_created(dbtransaction, new_entry):
    assert new_entry.created is not None


def test_id(dbtransaction, new_entry):
    assert new_entry.id is not None


def test_post_title(dbtransaction, new_entry):
    assert new_entry.title is not None


def test_post_text(dbtransaction, new_entry):
    assert new_entry.text is not None
