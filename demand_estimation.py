import shapefile
import math


def point_in_box(point_coord: list[float, float], box_corner_top_left: list[float, float],
                 box_corner_bottom_right:list[float, float]) -> bool:
    return (box_corner_top_left[0] <= point_coord[0] < box_corner_bottom_right[0]) and \
           (box_corner_top_left[1] <= point_coord[1] < box_corner_bottom_right[1])


def calculate_block_center_distance(stop_coordinate: list[float, float], block_side_length: float, block_no_x: int,
                                    block_no_y: int, min_xy: list[float, float]) -> float:
    box_center_x = min_xy[0] + block_side_length * (block_no_x + 0.5)
    box_center_y = min_xy[1] + block_side_length * (block_no_y + 0.5)
    return math.sqrt((stop_coordinate[0]-box_center_x)**2 + (stop_coordinate[1]-box_center_y)**2 )


def demand_estimation(transitstop_shapefile: str, total_population: int,  block_side_length: float,
                      stop_id_to_filter: list[int] = []) -> dict[int, int]:
    stop_coordinate_dict = {}
    stop_block_id_dict = {}
    stop_in_block_count_dict = {}
    stop_fraction_in_block_dict = {}
    stop_block_center_distance_dict = {}
    block_stop_block_center_distance_sum_dict = {}

    demand_dict = {}

    sf = shapefile.Reader(transitstop_shapefile)
    assert sf.shapeType == 1

    shapes = sf.shapes()

    max_xy = [-math.inf, -math.inf]
    min_xy = [math.inf, math.inf]

    for shape in shapes:
        if shape._Shape__oid not in stop_id_to_filter:
            stop_coordinate_dict[shape._Shape__oid] = shape.points[0]

            if shape.points[0][0] < min_xy[0]:
                min_xy[0] = shape.points[0][0]
            if shape.points[0][1] < min_xy[1]:
                min_xy[1] = shape.points[0][1]
            if shape.points[0][0] > max_xy[0]:
                max_xy[0] = shape.points[0][0]
            if shape.points[0][1] > max_xy[1]:
                max_xy[1] = shape.points[0][1]

    min_area_side_length = min((max_xy[1] - min_xy[1]), (max_xy[0] - min_xy[0]))
    assert block_side_length < min_area_side_length,\
        "block side length must be smaller than {0}".format(min_area_side_length)

    for transit_stop_id in stop_coordinate_dict:
        transit_stop_coordinate = stop_coordinate_dict[transit_stop_id]

        assert transit_stop_coordinate[0] >= min_xy[0] and transit_stop_coordinate[1] >= min_xy[1],\
            ""
        assert transit_stop_coordinate[0] <= max_xy[0] and transit_stop_coordinate[1] <= max_xy[1]

        block_id_x = int((transit_stop_coordinate[0] - min_xy[0]) // block_side_length)
        block_id_y = int((transit_stop_coordinate[1] - min_xy[1]) // block_side_length)

        if (block_id_x, block_id_y) not in stop_in_block_count_dict:
            stop_in_block_count_dict[(block_id_x, block_id_y)] = 0
        stop_block_id_dict[transit_stop_id] = (block_id_x, block_id_y)
        stop_in_block_count_dict[(block_id_x, block_id_y)] += 1
        stop_block_center_distance_dict[transit_stop_id] = calculate_block_center_distance(
            stop_coordinate=stop_coordinate_dict[transit_stop_id], block_side_length=block_side_length,
            block_no_x=block_id_x, block_no_y=block_id_y, min_xy=min_xy)

    for transit_stop_id in stop_block_center_distance_dict:
        block_id_of_transit_stop = stop_block_id_dict[transit_stop_id]
        if block_id_of_transit_stop not in block_stop_block_center_distance_sum_dict:
            block_stop_block_center_distance_sum_dict[block_id_of_transit_stop] = 0
        block_stop_block_center_distance_sum_dict[block_id_of_transit_stop] += \
            stop_block_center_distance_dict[transit_stop_id]

    # print(len(stop_in_block_count_dict))
    total_transit_stop = len(stop_coordinate_dict)
    for block_id in stop_in_block_count_dict:
        stop_fraction_in_block_dict[block_id] = stop_in_block_count_dict[block_id] / total_transit_stop

    for transit_stop_id in stop_coordinate_dict:
        block_id = stop_block_id_dict[transit_stop_id]
        block_population = total_population * stop_fraction_in_block_dict[block_id]
        estimated_demand = block_population * stop_block_center_distance_dict[transit_stop_id] / block_stop_block_center_distance_sum_dict[block_id]
        demand_dict[transit_stop_id] = estimated_demand
    return demand_dict


if __name__ == "__main__":
    SHPFILE = "example_shpfile/example_busstop.shp"
    # for this data
    # map area rectangle has minimum side of length 74.79131886496475
    print(demand_estimation(SHPFILE, total_population=100000, block_side_length=10))
