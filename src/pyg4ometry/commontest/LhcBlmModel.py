import os as _os
import numpy as _np
import pyg4ometry.gdml as _gd

# import matplotlib.pyplot as _plt

TWO_PI = 2 * _np.pi

COLOURS = {
    "none": (0, 0, 0, 0),
    "steel": (224, 223, 219, 1),  # regular steel
    "steel-lowalpha": (224, 223, 219, 0.2),  # regular steel
    # "aluminium": (165, 167, 173, 1),
    "aluminium": (100, 140, 152, 1),  # blue steel
    "iron": (104, 126, 139, 1),
    "aluminium_oxide": (217, 185, 155, 1),  # beige ;)
    "nitrogen": (102, 153, 83, 0.005),  # light grass green
}

materialToColour = {'BLM_Nitrogen':COLOURS['nitrogen'],
                    'BLM_Nitrogen_Active':COLOURS['nitrogen'],
                    'Al203':COLOURS['aluminium_oxide'],
                    'G4_Galactic':COLOURS['none'],
                    'nitrogen':COLOURS['nitrogen'],
                    'G4_STAINLESS-STEEL':COLOURS['steel-lowalpha'],
                    'aluminium':COLOURS['aluminium'],
                    'oxygen':(100,30,200,0.05),
                    'G4_Al':COLOURS['aluminium']
                    }


def assign_colour(lv, colour):
    colour_val = COLOURS.get(colour, (128, 128, 128, 1))
    colour_norm = [v / 255. for v in colour_val[:3]] + [colour_val[3]]
    col_string = "{} {} {} {}".format(*colour_norm)
    aux_tag = _gd.Auxiliary("colour", col_string, registry=lv.registry)
    lv.addAuxiliaryInfo(aux_tag)


def is_convex_polygon(polygon):
    """Return True if the polynomial defined by the sequence of 2D
    points is 'strictly convex': points are valid, side lengths non-
    zero, interior angles are strictly between zero and a straight
    angle, and the polygon does not intersect itself.

    NOTES:  1.  Algorithm: the signed changes of the direction angles
                from one side to the next side must be all positive or
                all negative, and their sum must equal plus-or-minus
                one full turn (2 pi radians). Also check for too few,
                invalid, or repeated points.
            2.  No check is explicitly done for zero internal angles
                (180 degree direction-change angle) as this is covered
                in other ways, including the `n < 3` check.
    """
    try:  # needed for any bad points or direction changes
        # Check for too few points
        if len(polygon) < 3:
            return False
        # Get starting information
        old_x, old_y = polygon[-2]
        new_x, new_y = polygon[-1]
        new_direction = _math.atan2(new_y - old_y, new_x - old_x)
        angle_sum = 0.0
        # Check each point (the side ending there, its angle) and accum. angles
        for ndx, newpoint in enumerate(polygon):
            # Update point coordinates and side directions, check side length
            old_x, old_y, old_direction = new_x, new_y, new_direction
            new_x, new_y = newpoint
            new_direction = _math.atan2(new_y - old_y, new_x - old_x)
            if old_x == new_x and old_y == new_y:
                return False  # repeated consecutive points
            # Calculate & check the normalized direction-change angle
            angle = new_direction - old_direction
            if angle <= -_np.pi:
                angle += TWO_PI  # make it in half-open interval (-Pi, Pi]
            elif angle > _np.pi:
                angle -= TWO_PI
            if ndx == 0:  # if first time through loop, initialize orientation
                if angle == 0.0:
                    return False
                orientation = 1.0 if angle > 0.0 else -1.0
            else:  # if other time through loop, check orientation is stable
                if orientation * angle <= 0.0:  # not both pos. or both neg.
                    return False
            # Accumulate the direction-change angle
            angle_sum += angle
        # Check that the total number of full turns is plus-or-minus 1
        return abs(round(angle_sum / TWO_PI)) == 1
    except (ArithmeticError, TypeError, ValueError):
        return False  # any exception means not a proper convex polygon


def rotate_point(xy, angle):
    x = xy[0]
    y = xy[1]

    angle = -angle
    x_new = x * _np.cos(angle) - y * _np.sin(angle)
    y_new = x * _np.sin(angle) + y * _np.cos(angle)

    return x_new, y_new


def circle_points(r, cx=0, cy=0, sa=0., ea=2 * _np.pi, npoints=30):
    points = []
    for theta in _np.linspace(sa, ea, npoints):
        x = cx + r * _np.sin(theta)
        y = cy + r * _np.cos(theta)
        points.append((x, y))

    return _np.array(points)


def electrode_profile():
    # Aluminium electrode
    ele_dia = 75
    ele_rad = ele_dia / 2.
    ele_cut_rad = 8.5  # Cutout radius for electrode
    ele_tap_rad = 3  # Cutout taper radius
    ele_cut_sa = _np.deg2rad(0)  # Starting angle for the cuts
    ele_cut_da = _np.deg2rad(120)  # Angular separation between cuts
    ele_cut_pos = 63 / 2.  # Radial position of cut centre
    ncuts = 3  # Number of cutouts

    electrode_points = []

    cutouts = []
    for i in range(ncuts):
        # Make a segment of the elecrode with cutout and taper
        angle = 0
        cx = ele_cut_pos * _np.sin(angle)
        cy = ele_cut_pos * _np.cos(angle)

        cut_angle_halfspan = ele_cut_rad / ele_cut_pos
        tap_angle_halfspan = ele_tap_rad / (ele_cut_pos + ele_tap_rad)

        left_tap_angle = angle - cut_angle_halfspan - tap_angle_halfspan
        right_tap_angle = angle + cut_angle_halfspan + tap_angle_halfspan

        cxl = (ele_cut_pos + ele_tap_rad) * _np.sin(left_tap_angle)
        cyl = (ele_cut_pos + ele_tap_rad) * _np.cos(left_tap_angle)

        cxr = (ele_cut_pos + ele_tap_rad) * _np.sin(right_tap_angle)
        cyr = (ele_cut_pos + ele_tap_rad) * _np.cos(right_tap_angle)

        offs = 0.1
        taper_points_left = circle_points(ele_tap_rad, cxl, cyl,
                                          offs, _np.pi / 2 - offs)

        cutout_points = circle_points(ele_cut_rad, cx, cy, 3 * _np.pi / 2 - offs, _np.pi / 2 + offs)

        taper_points_right = circle_points(ele_tap_rad, cxr, cyr,
                                           3 * _np.pi / 2 + offs, 2 * _np.pi - offs)

        electrode_arc_points = circle_points(ele_rad, 0, 0, right_tap_angle,
                                             ele_cut_da - cut_angle_halfspan - tap_angle_halfspan)

        # Rotate the ready segment to position
        angle = ele_cut_sa + i * ele_cut_da

        # cutout_points = _np.array([rotate_point(pt, angle) for pt in cutout_points])
        # taper_points_left = _np.array([rotate_point(pt, angle) for pt in taper_points_left])
        # taper_points_right = _np.array([rotate_point(pt, angle) for pt in taper_points_right])
        # electrode_arc_points = _np.array([rotate_point(pt, angle) for pt in electrode_arc_points])

        cutout_points = [rotate_point(pt, angle) for pt in cutout_points]
        taper_points_left = [rotate_point(pt, angle) for pt in taper_points_left]
        taper_points_right = [rotate_point(pt, angle) for pt in taper_points_right]
        electrode_arc_points = [rotate_point(pt, angle) for pt in electrode_arc_points]

        # Quite some difficulty in getting the point ordering correct
        segment_points = []
        electrode_points += taper_points_left
        electrode_points += cutout_points
        electrode_points += taper_points_right
        electrode_points += electrode_arc_points

        electrode_points += segment_points

    electrode_points = _np.array(electrode_points)

    # _plt.plot(_np.array(electrode_points)[:, 0], _np.array(electrode_points)[:, 1])
    # ax = _plt.gca()
    # ax.set_aspect("equal")
    # _plt.show()

    return _np.array(electrode_points)


def make_lhc_blm(vis=False, interactive=False, n_slice=16):

    import math as _math
    import pyg4ometry.gdml as _gd
    import pyg4ometry.geant4 as _g4
    import pyg4ometry.visualisation as _vi

    reg = _g4.Registry()

    # defines
    zero = _gd.Constant("zero", 0, reg)
    twopi = _gd.Constant("twopi", "2*pi", reg)

    safety_def = _gd.Constant("safety", 1e-8, reg)  # 10 pm safety

    safety = 1e-8

    # General numbers
    n_electrodes = 61

    # World volume dimensions
    world_z = 490
    world_x = 90
    world_y = 90

    # Outermost dimensions
    blm_len = 489
    blm_dia = 88.9
    blm_rad = blm_dia / 2.

    blm_radius = 62
    safety = 1.e-3

    # End cap, start
    endcap_s_rad = blm_rad
    endcap_s_len = 6

    # End cap, end
    endcap_e_rad = blm_rad
    endcap_e_len = 8

    # Tank dimensions - not including end caps
    tank_len = blm_len - endcap_s_len - endcap_e_len
    tank_thickness = 2
    tank_r_out = blm_rad
    tank_r_in = tank_r_out - tank_thickness

    # Outgassed spacers
    spacer_notch_w = 10
    spacer_notch_h = 2
    spacer_r_out = 7. / 2
    spacer_r_in = 4. / 2

    # 2 types of spacers
    spacer_a_l = 12
    spacer_a_notch_l = 5

    spacer_b_l = 18.25
    spacer_b_notch_l = 8

    # Support rods
    rod_r = spacer_r_in
    rod_l = spacer_a_l = 12

    # Electrodes
    electrode_l = 0.5
    electrode_sep = 5  # Need to check this number
    ele_dia = 75
    ele_rad = ele_dia / 2.
    ele_cut_rad = 8.5  # Cutout radius for electrode
    ele_tap_rad = 3  # Cutout taper radius
    ele_cut_sa = _np.deg2rad(0)  # Starting angle for the cuts
    ele_cut_da = _np.deg2rad(120)  # Angular separation between cuts
    ele_cut_pos = 63 / 2.  # Radial position of cut centre
    ncuts = 3  # Number of cutouts

    # electrode_points = electrode_profile()
    # electrode_zplanes = [[-electrode_l/2., (1, 1), 1],
    #                      [electrode_l/2., (1, 1), 1]]

    # Alumine insulators
    ins_l = 12
    ins_dia = 84
    ins_rad = ins_dia / 2.
    ins_hole_rad = 19 / 2.
    ins_cut_rad = 20
    ins_cut_pos = 56  # Radial position of cut centre
    ins_cut_angles = [_np.deg2rad(ang) for ang in [30, 150, 210, 330]]

    # Active gas dimensions - gas between electrodes
    # No gas outside the outer two electrodes
    active_gas_r = 38.25  # Gives 4% larger volume than the one covered by the electrodes
    active_gas_l = 31 * electrode_l + 31 * spacer_a_l
    active_gas_zpos = -tank_len / 2 + active_gas_l / 2. + 55 + electrode_l
    # active_gas_zpos = 0#-tank_len/2. + active_gas_l/2. + 55 + spacer_a_l

    # Materials
    blm_gas_material = _g4.MaterialCompound("BLM_Nitrogen", 0.0012506, 1, reg)
    n = _g4.ElementSimple("nitrogen", "N", 7, 14.0)
    blm_gas_material.add_element_natoms(n, 2)

    blm_active_gas_material = _g4.MaterialCompound("BLM_Nitrogen_Active", 0.0012506, 1, reg)
    blm_active_gas_material.add_element_natoms(n, 2)

    insulator_material = _g4.MaterialCompound("Al203", 3.98, 2, reg)
    ae = _g4.ElementSimple("aluminium", "Al", 13, 27.)
    oe = _g4.ElementSimple("oxygen", "O", 8, 16.0)
    insulator_material.add_element_natoms(ae, 2)
    insulator_material.add_element_natoms(oe, 3)

    # Construct the geometry objects

    # World
    wx = _gd.Constant("wx", world_x, reg)
    wy = _gd.Constant("wy", world_y, reg)
    wz = _gd.Constant("wz", world_z + 2, reg)

    world_solid = _g4.solid.Box("world_solid", wx, wy, wz, reg, "mm")
    world_material = _g4.Material(name="G4_Galactic")
    world_lv = _g4.LogicalVolume(world_solid, world_material, "world_lv", reg)

    # Nitrogen gas volume
    gas_len = _gd.Constant("gas_len", blm_len + safety + 2, reg)
    gas_r = _gd.Constant("gas_r", blm_rad + safety, reg)

    gas_solid = _g4.solid.Tubs("gas_volume", zero, gas_r, gas_len, zero, twopi,
                               reg, "mm", "rad", nslice=n_slice)

    gas_material = blm_gas_material
    gas_lv = _g4.LogicalVolume(gas_solid, gas_material, "gas_lv", reg)
    assign_colour(gas_lv, "nitrogen")
    gas_pv = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0],
                                gas_lv, "gas_pv1", world_lv, reg)

    # Active gas volume
    active_gas_len = _gd.Constant("active_gas_len", active_gas_l + safety, reg)
    active_gas_r = _gd.Constant("active_gas_r", active_gas_r + safety, reg)

    active_gas_solid = _g4.solid.Tubs("active_gas_volume", zero, active_gas_r, active_gas_len,
                                      zero, twopi, reg, "mm", "rad", nslice=n_slice)

    active_gas_material = blm_active_gas_material
    active_gas_lv = _g4.LogicalVolume(active_gas_solid, active_gas_material, "active_gas_lv", reg)
    assign_colour(active_gas_lv, "nitrogen")
    gas_pv = _g4.PhysicalVolume([0, 0, 0], [0, 0, active_gas_zpos],
                                active_gas_lv, "active_gas_pv1", gas_lv, reg)

    # Outer tank
    tank_z = _gd.Constant("tank_len", tank_len + safety, reg)
    tank_rin = _gd.Constant("tank_r_in", tank_r_in + safety, reg)
    tank_rout = _gd.Constant("tank_r_out", tank_r_out - safety, reg)

    tank_solid = _g4.solid.Tubs("tank", tank_rin, tank_rout, tank_z, zero, twopi,
                                reg, "mm", "rad", nslice=n_slice)

    tank_material = _g4.Material(name="G4_STAINLESS-STEEL")

    tank_lv = _g4.LogicalVolume(tank_solid, tank_material, "tank_lv", reg)
    assign_colour(tank_lv, "steel-lowalpha")
    tank_pv = _g4.PhysicalVolume([0, 0, 0], [0, 0, 0], tank_lv, "tank_pv1", gas_lv, reg)

    # End cap at the start of the blm
    endcap_s_z = _gd.Constant("encap_s_len", endcap_s_len - safety, reg)
    endcap_s_r = _gd.Constant("encap_s_radius", endcap_s_rad - safety, reg)

    endcap_s_solid = _g4.solid.Tubs("endcap_s", zero, endcap_s_r, endcap_s_z, zero, twopi,
                                    reg, "mm", "rad", nslice=n_slice)

    endcap_s_material = _g4.Material(name="G4_STAINLESS-STEEL")

    endcap_s_lv = _g4.LogicalVolume(endcap_s_solid, endcap_s_material, "endcap_s_lv", reg)
    assign_colour(endcap_s_lv, "steel")

    endcap_s_pos = [0, 0, -tank_len / 2. - endcap_s_len / 2.]
    endcap_s_pv = _g4.PhysicalVolume([0, 0, 0], endcap_s_pos,
                                     endcap_s_lv, "endcap_s_pv1", gas_lv, reg)

    # End cap at the end of the blm
    endcap_e_z = _gd.Constant("encap_e_len", endcap_e_len - safety, reg)
    endcap_e_r = _gd.Constant("encap_e_radius", endcap_e_rad - safety, reg)

    endcap_e_solid = _g4.solid.Tubs("endcap_e", zero, endcap_e_r, endcap_e_z, zero, twopi,
                                    reg, "mm", "rad", nslice=n_slice)

    endcap_e_material = _g4.Material(name="G4_STAINLESS-STEEL")

    endcap_e_lv = _g4.LogicalVolume(endcap_e_solid, endcap_e_material, "endcap_e_lv", reg)
    assign_colour(endcap_e_lv, "steel")

    endcap_e_pos = [0, 0, + tank_len / 2. + endcap_e_len / 2.]
    endcap_e_pv = _g4.PhysicalVolume([0, 0, 0], endcap_e_pos,
                                     endcap_e_lv, "endcap_e_pv1", gas_lv, reg)

    # Alumine insulator
    insulator_z = _gd.Constant("insulator_len", ins_l - safety, reg)
    insulator_r = _gd.Constant("insulator_radius", ins_rad - safety, reg)
    insulator_cut_r = _gd.Constant("insulator_cut_r", ins_cut_rad - safety, reg)
    insulator_hole_r = _gd.Constant("insulator_hole_r", ins_hole_rad - safety, reg)

    insulator_base = _g4.solid.Tubs("insulator_base", zero, insulator_r, ins_l,
                                    zero, twopi, reg, "mm", "rad", nslice=n_slice)

    insulator_cut = _g4.solid.Tubs("insulator_cut", zero, insulator_cut_r, ins_l + 3,
                                   zero, twopi, reg, "mm", "rad", nslice=n_slice)

    insulator_hole = _g4.solid.Tubs("insulator_hole", zero, insulator_hole_r,
                                    ins_l + 3, zero, twopi,
                                    reg, "mm", "rad", nslice=n_slice)

    # Make the cuts on the side and the hole in the middle
    interim_solid = insulator_base
    for i, angle in enumerate(ins_cut_angles):
        name = "insulator_interim_{}".format(i)
        cut_cx = ins_cut_pos * _np.sin(angle)
        cut_cy = ins_cut_pos * _np.cos(angle)
        cut_tra = [[0, 0, 0], [cut_cx, cut_cy, -0.5]]
        interim_solid = _g4.solid.Subtraction(name, interim_solid, insulator_cut,
                                              cut_tra, reg, "mm")

    insulator_solid = _g4.solid.Subtraction("insulator_solid", interim_solid, insulator_hole,
                                            [[0, 0, 0], [0, 0, -0.5]], reg, "mm")

    insulator_lv = _g4.LogicalVolume(insulator_solid, insulator_material, "insulator_lv", reg)
    assign_colour(insulator_lv, "aluminium_oxide")

    insulator_pos1 = [0, 0, - tank_len / 2. + ins_l / 2. + 43. - safety]
    insulator_pos2 = [0, 0,
                      - tank_len / 2. + ins_l / 2. + 43. + 31 * electrode_l + 32 * spacer_a_l + safety]
    insulator_pv1 = _g4.PhysicalVolume([0, 0, 0], insulator_pos1,
                                       insulator_lv, "insulator_pv1", gas_lv, reg)
    insulator_pv2 = _g4.PhysicalVolume([0, 0, 0], insulator_pos2,
                                       insulator_lv, "insulator_pv2", gas_lv, reg)

    # Electrode

    ############################################################################################
    # Using extruded solids - currently doesn't work so well
    # electrode_solid = _g4.solid.ExtrudedSolid("electrode_solid", electrode_points,
    #                                           electrode_zplanes, reg, "mm")

    ############################################################################################
    # Using tubs with cutouts - doesn't replicate the cut tapering
    electrode_solid = _g4.solid.Tubs("electrode_base", zero, ele_rad, electrode_l - safety_def,
                                     zero, twopi, reg, "mm", "rad", nslice=n_slice)

    electrode_cut = _g4.solid.Tubs("electrode_cut", zero, ele_cut_rad, electrode_l + 1,
                                   zero, twopi, reg, "mm", "rad", nslice=n_slice)

    ele_cut_angles = [_np.deg2rad(ang) for ang in (0, 120, 240)]
    for i, angle in enumerate(ele_cut_angles):
        name = "electrode_interim_{}".format(i)
        cut_cx = ele_cut_pos * _np.sin(angle)
        cut_cy = ele_cut_pos * _np.cos(angle)
        cut_tra = [[0, 0, 0], [cut_cx, cut_cy, 0]]
        electrode_solid = _g4.solid.Subtraction(name, electrode_solid, electrode_cut,
                                                cut_tra, reg, "mm")
    ##########################################################################################
    electrode_material = _g4.Material(name="G4_Al")
    electrode_lv = _g4.LogicalVolume(electrode_solid, electrode_material, "electrode_lv", reg)
    assign_colour(electrode_lv, "aluminium")

    # Outgassed spacer
    sp_a_base = _g4.solid.Tubs("spacer_a_base", spacer_r_in + safety, spacer_r_out - safety,
                               spacer_a_l, 0, 2 * _np.pi, reg, "mm", "rad", nslice=n_slice)

    sp_a_notch = _g4.solid.Box("spacer_a_notch", spacer_notch_w,
                               spacer_notch_h, spacer_a_notch_l, reg, "mm")

    sp_a_notch1_tra = [[0, 0, 0], [0, 0, spacer_a_l / 2. - spacer_a_notch_l / 2.]]
    sp_a_int = _g4.solid.Subtraction("spacer_a_interim", sp_a_base, sp_a_notch,
                                     sp_a_notch1_tra, reg, "mm")

    sp_a_notch2_tra = [[0, 0, _np.pi / 2], [0, 0, -spacer_a_l / 2. + spacer_a_notch_l / 2.]]
    spacer_a_solid = _g4.solid.Subtraction("spacer_a_solid", sp_a_int, sp_a_notch,
                                           sp_a_notch2_tra, reg, "mm")

    # In reality, this is a AlMgSi alloy, but it is ~97.5% Al
    spacer_a_material = _g4.Material(name="G4_Al")
    spacer_a_lv = _g4.LogicalVolume(spacer_a_solid, spacer_a_material, "spacer_a_lv", reg)
    assign_colour(spacer_a_lv, "iron")

    # Spacer steel core (nominally those are long support rods that also intesect the electrodes)
    support_rod_solid = _g4.solid.Tubs("support_rod", zero, rod_r - safety,
                                       rod_l - safety, 0, 2 * _np.pi, reg,
                                       "mm", "rad", nslice=n_slice)

    support_rod_material = _g4.Material(name="G4_STAINLESS-STEEL")
    support_rod_lv = _g4.LogicalVolume(support_rod_solid, support_rod_material,
                                       "support_rod_lv", reg)
    assign_colour(support_rod_lv, "steel")

    # Make the first set of electrodes and spacers
    start_pos = 55
    start_angle = 0
    electrode_cut_pos = 63 / 2.
    step_angle = _np.deg2rad(120)

    for i in range(31):
        for j in range(3):
            x = electrode_cut_pos * _np.sin(j * step_angle + step_angle / 2.)
            y = electrode_cut_pos * _np.cos(j * step_angle + step_angle / 2.)
            # spacer_zpos = -tank_len/2. + start_pos + i*(spacer_a_l + electrode_l) + spacer_a_l/2.
            spacer_zpos = -active_gas_len / 2. + i * (spacer_a_l + electrode_l) + spacer_a_l / 2.
            spacer_pos = [x, y, spacer_zpos]
            spacer_pv = _g4.PhysicalVolume([0, 0, 0], spacer_pos, spacer_a_lv,
                                           "spacer_pv_1_{}_{}".format(i, j), active_gas_lv, reg)
            support_rod_pv = _g4.PhysicalVolume([0, 0, 0], spacer_pos, support_rod_lv,
                                                "support_rod_pv_1_{}_{}".format(i, j),
                                                active_gas_lv, reg)

        if i == 30:
            continue

        # electrode_zpos = -tank_len/2. + start_pos + i * (spacer_a_l + electrode_l) \
        #                  + spacer_a_l + electrode_l/2.
        electrode_zpos = -active_gas_len / 2. + i * (
                    spacer_a_l + electrode_l) + spacer_a_l + electrode_l / 2.

        electrode_pos = [0, 0, electrode_zpos]

        electrode_pv = _g4.PhysicalVolume([0, 0, 0], electrode_pos,
                                          electrode_lv, "electrode_pv_1_{}".format(i),
                                          active_gas_lv, reg)

    # Make the second set of electrodes and spacers
    offset = 5.8  # The 5 is nominally a smaller, non-outgassed spacer, but those are ignored
    start_angle = _np.pi / 3
    electrode_cut_pos = 63 / 2.
    step_angle = _np.deg2rad(120)
    for i in range(31):
        for j in range(3):
            if i == 30:
                break
            x = electrode_cut_pos * _np.sin(start_angle + j * step_angle + step_angle / 2.)
            y = electrode_cut_pos * _np.cos(start_angle + j * step_angle + step_angle / 2.)
            spacer_zpos = -active_gas_len / 2. + offset + i * (spacer_a_l + electrode_l) + \
                          spacer_a_l / 2. + electrode_l

            spacer_pos = [x, y, spacer_zpos]
            spacer_pv = _g4.PhysicalVolume([0, 0, 0], spacer_pos,
                                           spacer_a_lv, "spacer_pv_2_{}_{}".format(i, j),
                                           active_gas_lv, reg)
            support_rod_pv = _g4.PhysicalVolume([0, 0, 0], spacer_pos, support_rod_lv,
                                                "support_rod_pv_2_{}_{}".format(i, j),
                                                active_gas_lv, reg)

        electrode_zpos = -active_gas_len / 2. + i * (
                    spacer_a_l + electrode_l) + electrode_l / 2. + offset
        electrode_pos = [0, 0, electrode_zpos]

        electrode_pv = _g4.PhysicalVolume([0, 0, start_angle], electrode_pos,
                                          electrode_lv, "electrode_pv_2_{}".format(i),
                                          active_gas_lv, reg)

    ##############################

    # set world volume
    reg.setWorld(world_lv.name)

    world_lv.checkOverlaps()

    # gdml output
    w = _gd.Writer()
    w.addDetector(reg)
    w.write("blm_model_colours.gdml")

    # visualisation
    v = 1
    if vis:
        #v = _vi.VtkViewerColouredMaterial()
        v = _vi.VtkViewer()
        v.addAxes(10)
        v.addLogicalVolume(reg.getWorldVolume())
        v.view(interactive=interactive)

    return world_lv


if __name__ == "__main__":
    # electrode_profile()
    make_lhc_blm(True, True)
