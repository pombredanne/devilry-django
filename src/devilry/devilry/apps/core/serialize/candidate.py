from ..models import Candidate
from .cache import serializedcache
from .user import serialize_user



def _serialize_cadidate(candidate):
    return {'id': candidate.id,
            'user': serialize_user(candidate.student),
            'candidate_id': candidate.candidate_id,
            'identifier': candidate.identifier}

serializedcache.add(_serialize_cadidate, {
    Candidate: None
})


def serialize_cadidate(candidate):
    return serializedcache.cache(_serialize_cadidate, candidate)

def serialize_cadidate_anonymous(candidate):
    serialized = serializedcache.cache(_serialize_cadidate, candidate)
    del serialized['user']
    return serialized
