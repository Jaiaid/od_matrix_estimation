# Origin-Destination  Matrix Estimation

demand_estimation.py contains function called demand_estimation
```
demand_estimation(transitstop_shapefile: str, total_population: int,  block_side_length: float, stop_id_to_filter: list[int] = []) -> dict[int, int]
```
### Output
A dictionary where,
- key: transit stop id according to shp file
- value: estimated demand

### Input
- transitstop_shapefile: str, file path of the shp file containing transit stops 
- total_population: int, \#population which will be served
- block_side_length: float, length of blocks to which map will be divided into
- stop_id_to_filter: list[int] = [], transit stop id (according to shp file) which will be ignored even if shp file has them

### Input condition
- block_side_length must be < smaller side of rectangle which encapsulate all the transit stop, otherwise assertion error will be thrown

### Example shp file
example_shpfile folder contains an example shp file for transit stop