# astrobucket
Astronomical data bucket 

# Usage

When you first request a query, `astrobucket` automatically run
xselect and return data as `astropy.table.Table` object.
After that, everytime you request the same query, `astrobucket` return
cache stored in `~/.astrobucket/cache`.

```python
import astrobucket

event_path = "dataset/example.evt"
client = astrobucket.Client(event_path, object_name="Earth",
                            satellite="EatchCapture", obsid="123456789")
event_table = client.request_event()
lc_table = client.request_curve(dt=0.1, enegy_range_key=(0.5, 10.0)
spec_table = client.request_spactrum(de=0.5, enegy_range_key=(0.5, 10.0)
```
