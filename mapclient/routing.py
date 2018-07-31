from channels.routing import route_class
from channels.staticfiles import StaticFilesConsumer
from mapclient import consumers


# routes defined for channel calls
# this is similar to the Django urls, but specifically for Channels
channel_routing = [
    route_class(consumers.MapConsumer, path=r"^/map/"),
]
