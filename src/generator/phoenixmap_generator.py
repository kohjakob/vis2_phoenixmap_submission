"""
Implementation of algorithm to generate Phoenixmaps. 
"""
from shapely import *
import scipy.interpolate as sci 
from shapely.validation import make_valid

import numpy as np
import math

import csv
import json
import os
import shutil


import matplotlib.pyplot as plt
import matplotlib.patches as pltp

def generate_phoenix_map(district_borders, buffer_size, num_segments, averaging_range, density_scale, circle_step_shrink_factor, listing_points, border_points):
    """
    Generates Phoenixmap with specified parameters from specified listings.

    Parameters
    ----------
    district_borders: bool
            If True generate Phoenixmap from specified district borders, if False generate Phoenixmap from convex hull
    buffer_size: float
            Size of buffer applied to convex hull/ district border
    num_segments: int
            Number of segments to divide fitted B-Spline curve for inscribed circle fitting 
    averaging_range: bool
            Number of segments to average over in weighted arithmetic mean calculation
    density_scale: bool
            Scale to map calculated density to line-thickness, dependend on size of overserved space
    circle_step_shrink_factor: float
            Shrinking of inscribed circle per iteration in inscribed circle fitting  
    listing_points: list(tuple(float, float))
            List of spatial data points (here district listings coordinates)
    border_points: list(tuple(float, float))
            List of area border data points (here district border coordinates)

    Returns
    ----------
    list(list(tuple(float, float)))
            Polygon of generated Phoenixmap
    """
    if not listing_points.is_empty:
        if district_borders:
            # Compute hull polygon from border points
            buffered_hull_polygon = Polygon(border_points.geoms).buffer(buffer_size)
        else:
            # Compute a buffered hull polygon
            buffered_hull_polygon = listing_points.convex_hull.buffer(buffer_size)

        # Fit a B-Spline (degree 3) curve through buffered convex hull
        bspline, param_range = sci.splprep(np.array(buffered_hull_polygon.exterior.coords).T, u=None, s=0.0, per=1, k=3) 
        
        # Get discrete segments on B-Spline curve
        segment_params = np.linspace(param_range.min(), param_range.max(), num_segments)
        bspline_xs, bspline_ys = sci.splev(segment_params, bspline, der=0)
        segments = list(zip(bspline_xs, bspline_ys))
        # Get polygon from segments
        bspline_polygon = Polygon(zip(bspline_xs, bspline_ys))

        # Compute tangents at segments midpoints
        mid_params = ((segment_params + np.roll(segment_params.copy(), 1, axis=0))/2)[1:]
        midpoint_xs, midpoint_ys = sci.splev(mid_params, bspline, der=0)
        midpoints = list(zip(midpoint_xs, midpoint_ys))
        tangent_xs, tangent_ys = sci.splev(mid_params, bspline, der=1)
        tangent_vecs = list(zip(tangent_xs, tangent_ys))

        # Compute curvature from segments midpoint tangents
        sec_deriv_xs, sec_deriv_ys = sci.splev(mid_params, bspline, der=2)
        sec_derivs = list(zip(sec_deriv_xs, sec_deriv_ys))
        curvatures = []
        for t, sd in zip(tangent_vecs, sec_derivs):
            cross_product = np.cross(t, sd)
            curvature = np.linalg.norm(cross_product) / (np.linalg.norm(t) ** 3)
            curvatures.append(curvature)

        # Compute normalized orthogonal vectors (pointing inside B-spline) from tangents 
        norm_tangent_vecs = [v/np.linalg.norm(v) for v in tangent_vecs]
        rotation_angle = math.radians(-90)
        norm_ortho_to_tangent_vecs = [(math.cos(rotation_angle)*v[0] - math.sin(rotation_angle)*v[1], math.sin(rotation_angle)*v[0] + math.cos(rotation_angle)*v[1]) for v in norm_tangent_vecs]
        
        # Compute upper bound for circle radius
        max_circle_radius = np.sqrt(buffered_hull_polygon.area / math.pi)
        max_curvature_radii = [c**-1 for c in curvatures]
        clamped_max_radius = [max(min(radius, max_circle_radius), 0) for radius in max_curvature_radii]

        # Compute inscribed circles
        circle_radii = []
        circle_centers = []
        for i, (midpoint, norm_ortho_to_tangent_vec, max_radius) in enumerate(zip(midpoints, norm_ortho_to_tangent_vecs, clamped_max_radius)):
            while True:
                circle_bound = (midpoint[0] + (norm_ortho_to_tangent_vec[0] * max_radius * 2), midpoint[1] + (norm_ortho_to_tangent_vec[1] * max_radius * 2))
                circle = minimum_bounding_circle(MultiPoint([midpoint, circle_bound]))

                # Check if circle fits inside B-Spline curve
                if circle.within(bspline_polygon) or max_radius < 0.0000005:
                    circle_center = (midpoint[0] + (norm_ortho_to_tangent_vec[0] * max_radius), midpoint[1] + (norm_ortho_to_tangent_vec[1] * max_radius))                  
                    circle_centers.append(circle_center)                          
                    circle_radii.append(max_radius)
                    break
                # Decrease radius until it fits inside B-spline polygon
                else:
                    max_radius = max_radius * circle_step_shrink_factor

        # Compute rectangular densities
        rectangle_densities = []
        rectangle_areas = []
        for i in range(len(midpoints) - 1):
            # Construct rectangle areas from circle centers and midpoints
            rectangle = Polygon([midpoints[i], circle_centers[i], circle_centers[i+1], midpoints[i+1], midpoints[i]])
            rectangle_area = rectangle.area
            rectangle_points = [point for point in list(listing_points.geoms) if within(point, rectangle)]
            rectangle_density = len(rectangle_points) / rectangle_area                   
            rectangle_densities.append(rectangle_density)
            rectangle_areas.append(rectangle_area)

        # Compute weighted moving average densities for segments
        wam_segment_densities = []
        rectangle_densities = np.concatenate((np.concatenate((rectangle_densities, rectangle_densities)), rectangle_densities))
        rectangle_areas = np.concatenate((np.concatenate((rectangle_areas, rectangle_areas)), rectangle_areas))
        number_of_circles = len(circle_centers)
        for i in range(number_of_circles, 2*number_of_circles):  # Start idx in "middle" run until "end of middle" 
            lower_range_limit = i - averaging_range
            upper_range_limit = i + averaging_range
            densities_for_average = rectangle_densities[lower_range_limit:upper_range_limit]
            weights_for_average = rectangle_areas[lower_range_limit:upper_range_limit]
            weights_for_average = weights_for_average + 10e-15 # Division by zero escape

            wam_segment_densities.append(np.average(densities_for_average, weights=weights_for_average))

        # Build outer polygon
        outline_polygon_outer = []
        border_polygon = []
        for i in range(len(midpoints)-1):
            segment_startpoint = midpoints[i]
            outline_polygon_outer.append(segment_startpoint)
            border_polygon.append(segment_startpoint)
        outline_polygon_outer.append(outline_polygon_outer[0])
    
        # Build inner polygon
        outline_polygon_inner_primary = []
        midpoints.reverse()
        wam_segment_densities.reverse()
        norm_ortho_to_tangent_vecs.reverse()

        segment_density = wam_segment_densities[0] * density_scale
        x = norm_ortho_to_tangent_vecs[0][0] * segment_density
        y = norm_ortho_to_tangent_vecs[0][1] * segment_density
        corner_point = (midpoints[0][0] + x, midpoints[0][1] + y)
        outline_polygon_inner_primary.append(corner_point)

        # Escape loops in inner polygon
        for i in range(len(midpoints)-1):
            segment_density = wam_segment_densities[i] * density_scale
            x = norm_ortho_to_tangent_vecs[i][0] * segment_density
            y = norm_ortho_to_tangent_vecs[i][1] * segment_density
            corner_point = (midpoints[i][0] + x, midpoints[i][1] + y)

            past_segment_lines = []
            line = LineString([outline_polygon_inner_primary[-1], corner_point])
            if len(past_segment_lines) >= 2:
                intersecting = False
                for line_to_check in past_segment_lines[:-1]:
                    if(line.intersects(line_to_check)):
                        intersecting = True
                        index = past_segment_lines.index(line_to_check)
                        intersection_point = line.intersection(line_to_check).coords[0]

                        outline_polygon_inner_primary = outline_polygon_inner_primary[:index+1]
                        past_segment_lines = past_segment_lines[:index]
                        
                        past_segment_lines.append(LineString([outline_polygon_inner_primary[-1], intersection_point]))
                        past_segment_lines.append(LineString([intersection_point, corner_point]))
                        outline_polygon_inner_primary.append(intersection_point)
                        outline_polygon_inner_primary.append(corner_point)
                        break
                if not intersecting:
                    past_segment_lines.append(line)
                    outline_polygon_inner_primary.append(corner_point)
            else:
                past_segment_lines.append(line)
                outline_polygon_inner_primary.append(corner_point)
            
        outline_polygon_inner_primary.append(outline_polygon_inner_primary[0])

        # Escape start/end loops in inner polygon to avoid artifacts
        inner_multi_polygons = make_valid(Polygon(outline_polygon_inner_primary))
        outline_polygon_inner = None
        max_polygon_area = 0
        if type(inner_multi_polygons) == MultiPolygon:
            for polygon in inner_multi_polygons.geoms:
                if polygon.area > max_polygon_area:
                    max_polygon_area = polygon.area
                    outline_polygon_inner = list(polygon.exterior.coords)
        else:
            outline_polygon_inner = list(inner_multi_polygons.exterior.coords)
        
                
        outline_polygon = outline_polygon_outer + outline_polygon_inner

        # Close polygon to avoid artifacts
        outline_polygon.append(outline_polygon_outer[-1])

        # Create final polygon
        shapely_polygon = Polygon(outline_polygon)
        outline_polygon= list(shapely_polygon.exterior.coords)

        # Debug plotting
        """ pltpolygon = pltp.Polygon(outline_polygon)
        fig, ax = plt.subplots()
        ax = plt.subplot()
        ax.set_aspect('equal', adjustable='box')
        ax.add_patch(pltpolygon)
        #ax.plot(bspline_xs, bspline_ys)
        ax.scatter([p.x for p in listing_points.geoms], [p.y for p in listing_points.geoms], s=1)
        plt.show() """
        
        return outline_polygon

def setup_and_generate():
    """
    Flush polygon directories before generation. Load district border and district listing data. 
    Start Phoenixmap generation tasks and save resulting polygons as json.
    """
    dir_path =  os.path.dirname(os.path.realpath(__file__))
    scale = 0.0000000001
    num_segments = 100
    wam_range = 10
    circle_shrink = 0.80

    # 1. Generate Phoenixmaps for the specified year_ranges for every districty
    with open(os.path.join(dir_path, 'ressources/district_borders.json')) as district_borders:
        districts = json.load(district_borders).keys()

        for year_range in  [(2009, 2013), (2009, 2017), (2009, 2021), (2013, 2017), (2013, 2021), (2017, 2021), (2009, 2009), (2013, 2013), (2017, 2017), (2021, 2021)]:
            from_year, to_year = year_range[0], year_range[1]

            # Flush result directory
            dir_name = os.path.join(dir_path, "../app/ressources/polygons_{}_{}".format(str(year_range[0]), str(year_range[1])))
            if os.path.exists(dir_name): 
                shutil.rmtree(dir_name) 
            os.makedirs(dir_name)
                
            for district in districts:

                year_range_points = []
                with open(os.path.join(dir_path, "ressources/district_listings.json")) as file:
                    data = json.load(file)
                    year_range_points = [Point(item['latitude'], item['longitude']) for item in data[district] if from_year <= int(item["host_since"][:4]) <= to_year]
                    year_range_points = MultiPoint(year_range_points)
                
                border_points = []
                with open(os.path.join(dir_path, "ressources/district_borders.json")) as file:
                    data = json.load(file)
                    json_points = [Point(item['latitude'], item['longitude']) for item in data[district]]
                    border_points = MultiPoint(json_points)
                
                district_borders = True
                buffer = 0
                polygon = generate_phoenix_map(district_borders, buffer, num_segments, wam_range, scale, circle_shrink, year_range_points, border_points)
                
                with open(os.path.join(dir_name, district + ".json"), "w") as district_listings:
                    json.dump(polygon, district_listings) 

    # 2. Generate Phoenixmaps for specified years for distrct "Bourse"

    # Flush result directories
    dir_name_convex = os.path.join(dir_path, "../app/ressources/polygons_bourse_year_convex_hull/")
    if os.path.exists(dir_name_convex): 
        shutil.rmtree(dir_name_convex) 
    os.makedirs(dir_name_convex)

    dir_name_borders = os.path.join(dir_path, "../app/ressources/polygons_bourse_year_district_borders/")
    if os.path.exists(dir_name_borders): 
        shutil.rmtree(dir_name_borders) 
    os.makedirs(dir_name_borders)

    for year in [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]:

        listing_points = []
        with open(os.path.join(dir_path, "ressources/district_listings.json")) as file:
            data = json.load(file)
            year_points = []
            year_points = [Point(item['latitude'], item['longitude']) for item in data["Bourse"] if int(item["host_since"][:4]) == year]
            listing_points = MultiPoint(year_points)
        
        border_points = []
        with open(os.path.join(dir_path, "ressources/district_borders.json")) as file:
            data = json.load(file)
            json_points = [Point(item['latitude'], item['longitude']) for item in data["Bourse"]]
            border_points = MultiPoint(json_points)

        # 2.1 Pheonixmap based on convex hull around district 
        if(len(border_points.geoms) > 3):
            district_borders = False
            buffer = 0
            scale = 0.0000000003
            polygon = generate_phoenix_map(district_borders, buffer, num_segments, wam_range, scale, circle_shrink, listing_points, border_points)
            with open(dir_name_convex+"/"+str(year)+".json", "w") as district_listings:
                json.dump(polygon, district_listings)

        # 2.2 Phoenixmap based on convex hull around district with buffer 0.001
        if(len(border_points.geoms) > 3):
            district_borders = True
            buffer = 0.001
            scale = 0.0000000003
            polygon = generate_phoenix_map(district_borders, buffer, num_segments, wam_range, scale, circle_shrink, listing_points, border_points)
            with open(dir_name_borders+"/"+str(year)+".json", "w") as district_listings:
                json.dump(polygon, district_listings)

if __name__ == "__main__":
    setup_and_generate()