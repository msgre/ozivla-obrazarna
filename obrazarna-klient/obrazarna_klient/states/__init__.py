from .intro import Intro
from .fadeout import Fadeout
from .zoom import Zoom
from .preview import Preview
from .upload import Upload


STATE_INTRO = 'intro'
STATE_FADEOUT = 'fadeout'
STATE_ZOOM = 'zoom'
STATE_PREVIEW = 'preview'
STATE_UPLOAD = 'upload'


STATES = {
    STATE_INTRO: Intro,
    STATE_FADEOUT: Fadeout,
    STATE_ZOOM: Zoom,
    STATE_PREVIEW: Preview,
    STATE_UPLOAD: Upload,
}
