
from datastructures.Shape import Shape
from datastructures.TrackableTypes import TrackableTypes
from interaction import Effect
from smath import smath


class Interaction:
    def __init__(self):
        # Flag to store, whether an item currently is carried
        self.is_carrying_entity = False
        self.is_carrying_file = False
        self.is_drawing = False
        pass

    def process(self, target_widget):
        # evaluations of potential interaction techniques
        # e.g. interaction regions, poinintg by touch, tangible as knob / slider
        self.__handle_touch_collision(target_widget.processed_trackables, target_widget)
        self.__handle_trackable_to_shape_collision(target_widget)
        self.__handle_shape_to_shape_collision(target_widget)
        self.__handle_trackable_to_trackable_collision(target_widget)
        self.__handle_brush_assignment(target_widget.processed_trackables, target_widget)


    def __handle_trackable_to_shape_overlap(self, trackable, region_overlaps, target_widget):
        region_overlaps[0].colliding_with_shape = True

        if region_overlaps[0].type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
            for q in target_widget.previous_processed_trackables:
                if q.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
                    if region_overlaps[0].id == q.id:
                        if q.emailed:
                            region_overlaps[0].emailed = True
                        else:
                            region_overlaps[0].emailed = False

                        if q.stored:
                            region_overlaps[0].stored = True
                        else:
                            region_overlaps[0].stored = False

        # Handle exactly two items overlapping
        if len(region_overlaps) == 2:
            if region_overlaps[1].effect is not None:
                if region_overlaps[0].type_id == TrackableTypes.FILE.value:
                    if region_overlaps[
                        1].effect.effect_type == Effect.EffectType.CONVEYOR_BELT.value:
                        region_overlaps[0].emailed = False
                        region_overlaps[0].stored = False
                        region_overlaps[0].delegated = False
                        region_overlaps[0].done_at_once = False
                        region_overlaps[0].show_icon()
                    else:
                        region_overlaps[0].is_on_conveyor_belt = False

        if region_overlaps[0].type_id == TrackableTypes.FILE.value:
            has_conveyor_belt_region = False
            is_magnified = False
            is_tagged = False

            is_overlapping_with_composite = False
            for p in region_overlaps[1:]:
                if isinstance(p.effect, Effect.CompositeBase):
                    if id(trackable) not in p.effect.known_items:
                        is_overlapping_with_composite = True

            # Prevent triggering single composite region on enter
            if is_overlapping_with_composite is False:
                for p in region_overlaps[1:]:
                    if p.effect is not None:
                        if p.effect.effect_type == Effect.EffectType.CONVEYOR_BELT.value:
                            if not region_overlaps[0].grabbed:
                                has_conveyor_belt_region = True

                        elif p.effect.effect_type == Effect.EffectType.MAGNIFICATION.value:
                            is_magnified = True
                            region_overlaps[0].is_transfer_magnified = False
                        elif p.effect.effect_type == Effect.EffectType.TAG.value:
                            is_tagged = True
                            region_overlaps[0].tagged = True

            if not has_conveyor_belt_region:
                region_overlaps[0].is_on_conveyor_belt = False

            if not is_magnified:
                region_overlaps[0].show_icon()

        if region_overlaps[0].type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
            for p in region_overlaps[1:]:
                if p.effect is not None:
                    if p.effect.effect_type == Effect.EffectType.TAG.value:
                        is_tagged = True
                        region_overlaps[0].tagged = True
                        target_widget.phys_tag = True


        InteractionRegion.action(region_overlaps, target_widget,
                                 target_widget.previous_concurrent_hands)


        self.__handle_trackable_to_multiple_conveyors_overlap(trackable, region_overlaps, target_widget)


    def __handle_trackable_drop(self, region_overlaps, trackable, target_widget):
        if region_overlaps[0].type_id == TrackableTypes.FILE.value:
            target_widget.on_email_delegate_storage_doAtOnce_left.emit(trackable.id)

            region_overlaps[0].emailed = False
            region_overlaps[0].stored = False
            region_overlaps[0].delegated = False
            region_overlaps[0].is_on_conveyor_belt = False
            region_overlaps[0].done_at_once = False

            if not region_overlaps[0].is_transfer_magnified:
                region_overlaps[0].show_icon()

        if region_overlaps[0].type_id == TrackableTypes.TANGIBLE.value:
            target_widget.initial_tangible_collision = False

    def __handle_trackable_to_multiple_conveyors_overlap(self, trackable, region_overlaps, target_widget):
        shapes = list(filter(lambda x: isinstance(x, Shape), region_overlaps))
        colliding_conveyor_belts = list(filter(lambda x: x.effect.effect_type == Effect.EffectType.CONVEYOR_BELT.value, shapes))
        if(len(colliding_conveyor_belts) > 1):
            # only change belt, if condition is True
            if trackable.previously_on_crossing is False \
                    and self.handle_conveyor_condition("is_review_accepted", trackable) is True\
                    and id( colliding_conveyor_belts[0]) not in trackable.previously_crossed_belts \
                    and id( colliding_conveyor_belts[1]) not in trackable.previously_crossed_belts:
                target_widget.stop_conveyor_belt_animation(trackable.id)
                trackable.is_on_conveyor_belt = False
                target_widget.on_conveyor_move_requested.emit(
                    trackable.center[0],
                    trackable.center[1],
                    trackable.id,
                    colliding_conveyor_belts[1].middle_line,
                    # TODO could we get this into a constant?
                    5000,
                    False,
                    False,
                    0
                )
                # trackable.is_on_conveyor_belt = True
                trackable.previously_on_crossing = True
                trackable.previously_crossed_belts = [] + [
                    id(colliding_conveyor_belts[0]),
                    id(colliding_conveyor_belts[1])
                ]
        else:
            trackable.previously_on_crossing = False

    def __detect_trackable_to_shape_overlaps(self, trackable, tracked_shape, drawn_shape, shape_mask, region_overlaps, target_widget):
        if trackable.type_id is not TrackableTypes.BUTTON.value and trackable.type_id is not TrackableTypes.TOUCH.value:
            if drawn_shape.effect is not None:
                if drawn_shape.effect.effect_type == Effect.EffectType.TAG.value:
                    if trackable.type_id == TrackableTypes.HAND.value or trackable.type_id == TrackableTypes.FILE.value or trackable.type_id == TrackableTypes.TANGIBLE.value or trackable.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
                        if drawn_shape.collides_with_via_aabb(
                                tracked_shape.aabb):
                            if shape_mask.collides_with(tracked_shape.roi):
                                region_overlaps.append(drawn_shape)
                    else:
                        return

                # Handle Conveyor Belt Collision
                if drawn_shape.effect.effect_type == Effect.EffectType.CONVEYOR_BELT.value:
                    if trackable.type_id == TrackableTypes.FILE.value:
                        if drawn_shape.collides_with_via_aabb(
                                tracked_shape.roi):
                            if shape_mask.collides_with(tracked_shape.roi):
                                drawn_shape.is_active = True
                                # TODO
                                #colliding_conveyor_belts.append(drawn_shape)
                                region_overlaps.append(drawn_shape)
                            else:
                                drawn_shape.is_active = False
                    elif trackable.type_id == TrackableTypes.HAND.value:
                        if drawn_shape.collides_with_via_aabb(
                                tracked_shape.aabb):
                            if shape_mask.collides_with(tracked_shape.aabb):
                                region_overlaps.append(drawn_shape)
                    elif trackable.type_id == TrackableTypes.TANGIBLE.value:
                        if drawn_shape.collides_with_via_aabb(
                                tracked_shape.aabb):
                            if shape_mask.collides_with(tracked_shape.roi):
                                region_overlaps.append(drawn_shape)
                else:
                    # Handle Palette Collision
                    if drawn_shape.effect.effect_type == Effect.EffectType.PALETTE.value:
                        if trackable.type_id == TrackableTypes.HAND.value:
                            if drawn_shape.is_palette_parent:
                                if drawn_shape not in region_overlaps:
                                    if drawn_shape.collides_with_via_aabb(
                                            tracked_shape.aabb):
                                        if shape_mask.collides_with(
                                                tracked_shape.roi):
                                            region_overlaps.append(drawn_shape)
                            else:
                                parent_shape = target_widget.drawn_shapes[
                                    drawn_shape.palette_parent]

                                if parent_shape not in region_overlaps:
                                    if drawn_shape.collides_with_via_aabb(
                                            tracked_shape.aabb):
                                        if shape_mask.collides_with(
                                                tracked_shape.roi):
                                            region_overlaps.append(parent_shape)
                    else:
                        if drawn_shape.collides_with_via_aabb(
                                tracked_shape.aabb):
                            if shape_mask.collides_with(tracked_shape.roi):
                                if trackable.type_id != TrackableTypes.HAND.value:
                                    drawn_shape.is_active = True

                                    region_overlaps.append(drawn_shape)
                        else:
                            if trackable.type_id != TrackableTypes.HAND.value:
                                drawn_shape.is_active = False
            else:
                if trackable.type_id == TrackableTypes.HAND.value:
                    if drawn_shape.collides_with_via_aabb(tracked_shape.aabb):
                        if shape_mask.collides_with(tracked_shape.roi):
                            region_overlaps.append(drawn_shape)

    def __handle_trackable_to_shape_collision(self, target_widget):
        trackables = target_widget.processed_trackables
        drawn_shapes = target_widget.drawn_shapes
        shape_masks = target_widget.masks
        # we need this in order to detect branches

        for trackable in trackables:
            trackable.set_parent_widget(target_widget)
            region_overlaps = [trackable]

            if trackable.type_id == TrackableTypes.FILE.value:
                tracked_shape = Shape(trackable.collision_roi)
            else:
                tracked_shape = Shape(trackable.roi)

            for i, drawn_shape in enumerate(drawn_shapes):
                shape_mask = shape_masks[i]

                # Handle DELETION to file collision
                # Quite hacky, but still works
                if drawn_shape.effect.effect_type == Effect.EffectType.DELETION.value:
                    if trackable.type_id == TrackableTypes.FILE.value:
                        if drawn_shape.collides_with_via_aabb(tracked_shape.aabb):
                            target_widget.delete_file(trackable.center)

                elif drawn_shape.effect.effect_type == Effect.EffectType.MAGNIFICATION.value:
                    if drawn_shape.collides_with_via_aabb(tracked_shape.aabb):
                        if shape_mask.collides_with(tracked_shape.roi):
                            if trackable.type_id == TrackableTypes.FILE.value:
                                target_widget.on_file_magnification_requested.emit(trackable.id, drawn_shape.effect.interval[0])

                # idk, why this only happens when shape is not movable
                if not drawn_shape.moveable:
                    self.__detect_trackable_to_shape_overlaps(trackable, tracked_shape, drawn_shape, shape_mask, region_overlaps, target_widget)
                else:
                    if trackable.type_id is TrackableTypes.TOUCH.value:
                        if drawn_shape.collides_with_via_aabb(tracked_shape.aabb):
                            if shape_mask.collides_with(tracked_shape.roi):
                                region_overlaps.append(drawn_shape)
                                target_widget.drawing = False

                    # if drawn_shape.attached:
                    if drawn_shape.effect.effect_type == Effect.EffectType.MAGNIFICATION.value or drawn_shape.effect.effect_type == Effect.EffectType.DELETION.value:
                        if trackable.type_id == TrackableTypes.FILE.value:
                            if drawn_shape.collides_with_via_aabb(tracked_shape.aabb):
                                if shape_mask.collides_with(tracked_shape.roi):
                                    drawn_shape.is_active = True
                                    region_overlaps.append(drawn_shape)

            #
            #
            # Handle recognized overlaps

            #
            #
            # Handle more than one items overlapping
            if len(region_overlaps) > 1:
                self.__handle_trackable_to_shape_overlap(trackable, region_overlaps, target_widget)
            # Handle no item overlapping
            else:
                self.__handle_trackable_drop(region_overlaps, trackable, target_widget)








    #

    def handle_conveyor_condition(self, type, file, param=None):
        if type is "has_tags":
            return file.tagged
        elif type is "is_review_accepted":
            return file.review_accepted
        # TODO: add other conditions here
        else:
            print("unhandled condition type reached:", type)
            return False


    def __handle_shape_to_shape_collision(self, target_widget):
        shape_masks = target_widget.masks
        
        if len(target_widget.drawn_shapes) > 1:
            for i in range(len(target_widget.drawn_shapes)):
                for k in range(i + 1, len(target_widget.drawn_shapes)):
                    
                    shape_a = target_widget.drawn_shapes[i]
                    shape_b = target_widget.drawn_shapes[k]
                    fx_a = shape_a.effect
                    fx_b = shape_b.effect
                    fxt_1 = Effect.EffectType(fx_a.effect_type)
                    fxt_2 = Effect.EffectType(fx_b.effect_type)

                    # This is quite hacky but does the trick for allowing
                    if shape_a.collides_with_via_aabb(shape_b.aabb):
                        # Palettes somehow provide collision feedback, since their single
                        # parts always collide with each other
                        if fxt_1 is not Effect.EffectType.PALETTE or fxt_2 is not Effect.EffectType.PALETTE:
                            # Trigger an action on continuous collision
                            if fxt_1 is Effect.EffectType.DELETION or fxt_2 is Effect.EffectType.DELETION:
                                if fxt_1 is Effect.EffectType.DELETION:
                                    if shape_masks[k].collides_with(shape_a.roi):
                                        target_widget.on_region_collision_deletion.emit(k)
                                else:
                                    if shape_masks[i].collides_with(shape_b.roi):
                                        target_widget.on_region_collision_deletion.emit(i)
                                return


                    # I have inserted the portion above, since it may be the quickest and easiest way
                    # Of deleting objects on drag. Some functions may be implemented as duplicates
                    else:
                        if target_widget.drawn_shapes[k].effect is not None and target_widget.drawn_shapes[k].effect.effect_type == Effect.EffectType.DELETION.value:
                            if target_widget.drawn_shapes[i].effect is not None and target_widget.drawn_shapes[i].effect.effect_type != Effect.EffectType.PALETTE.value:
                                if not target_widget.drawn_shapes[i].moveable and target_widget.drawn_shapes[i].dropped:
                                    if target_widget.drawn_shapes[i].collides_with_via_aabb(target_widget.drawn_shapes[k].aabb):
                                        if target_widget.masks[k].collides_with(target_widget.drawn_shapes[i].roi):
                                            target_widget.on_region_collision_deletion.emit(i)
                                            return
                                else:
                                    if target_widget.drawn_shapes[i].effect.effect_type == Effect.EffectType.DELETION.value:
                                        if target_widget.drawn_shapes[i].attached:
                                            if target_widget.drawn_shapes[i].collides_with_via_aabb(target_widget.drawn_shapes[k].aabb):
                                                if target_widget.masks[k].collides_with(target_widget.drawn_shapes[i].roi):
                                                    target_widget.on_region_collision_deletion.emit(i)
                                                    return

                                    elif target_widget.drawn_shapes[k].effect.effect_type == Effect.EffectType.DELETION.value:
                                        if target_widget.drawn_shapes[k].attached:
                                            if target_widget.drawn_shapes[k].collides_with_via_aabb(target_widget.drawn_shapes[i].aabb):
                                                if target_widget.masks[k].collides_with(target_widget.drawn_shapes[i].roi):
                                                    target_widget.on_region_collision_deletion.emit(i)

                                                    return

                        elif target_widget.drawn_shapes[i].effect is not None and target_widget.drawn_shapes[i].effect.effect_type == Effect.EffectType.DELETION.value:
                            if target_widget.drawn_shapes[k].effect is not None and target_widget.drawn_shapes[k].effect.effect_type != Effect.EffectType.PALETTE.value:
                                if not target_widget.drawn_shapes[k].moveable and target_widget.drawn_shapes[k].dropped:
                                    if target_widget.drawn_shapes[k].collides_with_via_aabb(target_widget.drawn_shapes[i].aabb):
                                        if target_widget.masks[i].collides_with(target_widget.drawn_shapes[k].roi):
                                            target_widget.on_region_collision_deletion.emit(k)

                                            return
                                else:
                                    if target_widget.drawn_shapes[i].effect.effect_type == Effect.EffectType.DELETION.value:
                                        if target_widget.drawn_shapes[i].attached:
                                            if target_widget.drawn_shapes[k].collides_with_via_aabb(target_widget.drawn_shapes[i].aabb):
                                                if target_widget.masks[i].collides_with(target_widget.drawn_shapes[k].roi):
                                                    target_widget.on_region_collision_deletion.emit(k)

                                                    return

    def __handle_touch_collision(self, trackables, target_widget):
        for t1 in target_widget.previous_concurrent_touches_1:
            if t1.id not in [i.id for i in target_widget.concurrent_touches]:
                if not t1.is_holding():
                    self.__handle_touch_tap(t1, trackables, target_widget)
                    self.__handle_touch_tap_region(t1, target_widget)
            else:
                if t1.is_holding():
                    #if not target_widget.drawing:
                    self.__handle_touch_hold_drag(t1, trackables, target_widget)
                    self.__handle_touch_hold_drag_regions(t1, target_widget)

    def __handle_touch_tap(self, touch, trackables, target_widget):

        touch_shape = Shape(touch.roi)

        TouchTapEvent.action_touch(touch, target_widget)

        for t in trackables:
            if t.type_id == TrackableTypes.FILE.value:
                if not True in [s.moveable for s in target_widget.drawn_shapes]:
                    file_shape = Shape(t.roi)

                    if touch_shape.collides_with_via_aabb(file_shape.aabb):
                        if target_widget.has_transfer_effect_stored:
                            TouchTapEvent.action_file_transfer(t, touch, target_widget)

                            return
                        else:
                            t.previously_touched = True
                            TouchTapEvent.action_file(t, touch)

                            return



            elif t.type_id == TrackableTypes.BUTTON.value:
                button_shape = Shape(t.roi)
                t.previously_touched = True

                if touch_shape.collides_with_via_aabb(button_shape.aabb):
                    TouchTapEvent.action_button(t, touch)
                    return

        if len(target_widget.active_menus) > 0:
            TouchTapEvent.action(touch, target_widget)

    def __handle_touch_tap_region(self, touch, target_widget):
        touch_shape = Shape(touch.roi)

        for i, shape in enumerate(target_widget.drawn_shapes):
            if shape.effect.effect_type == Effect.EffectType.PALETTE.value:
                if not shape.moveable:
                    if not shape.palette_parent:
                        if target_widget.masks[i].collides_with(touch_shape.roi):
                            TouchTapEvent.action_region(touch, target_widget, i)
                            return True
            else:
                if target_widget.masks[i].collides_with(touch_shape.roi):
                    # shape.moveable = True
                    # self.is_carrying_entity = True
                    pass
            """
            else:
                if not shape.moveable and target_widget.has_transfer_effect_stored:
                    if target_widget.transfer_effect is not None:
                        if target_widget.masks[i].collides_with(touch_shape.roi):
                            TouchTapEvent.action_region_transfer(touch, target_widget, i)

                            return True
            """

        return False


    # Handle drag files etc.
    def __handle_touch_hold_drag(self, touch, trackables, target_widget):
        touch_shape = Shape(touch.roi)

        drag_candidates = []

        for t in trackables:
            if t.type_id == TrackableTypes.FILE.value:
                if not True in [s.moveable for s in target_widget.drawn_shapes]:
                    file_shape = Shape(t.roi)

                    t.previously_touched = True

                    if touch_shape.collides_with_via_aabb(file_shape.aabb):
                        drag_candidates.append(t)

        if len(drag_candidates) > 0:
            for i, _t in enumerate(drag_candidates):
                if touch.id == _t.touch_id:
                    TouchHoldDragEvent.action(_t, touch)
                    target_widget.currently_dragged_file = _t
                    return

            TouchHoldDragEvent.action(drag_candidates[-1], touch)
            target_widget.currently_dragged_file = drag_candidates[-1]
        else:
            target_widget.currently_dragged_file = None

    def __handle_touch_hold_drag_regions(self, touch, target_widget):
        touch_shape = Shape(touch.roi)

        for idx, shape in enumerate(target_widget.drawn_shapes):
            if shape.moveable:
                if touch_shape.collides_with_via_aabb(shape.aabb):
                    TouchHoldDragEvent.action_region(touch, target_widget, idx)
            elif shape.effect.effect_type != Effect.EffectType.PALETTE.value and shape.effect.effect_type is not Effect.EffectType.CONVEYOR_BELT.value:
                # kinda called on "touch down", first contact
                if touch_shape.collides_with_via_aabb(shape.aabb) and self.is_carrying_entity is False and target_widget.currently_dragged_file is None:
                    #TouchHoldDragEvent.action_region_transfer(touch, target_widget, idx)
                    shape.moveable = True
                    self.is_carrying_entity = True
                    pass


    # Here, widget callbacks can be triggered
    def __handle_trackable_to_trackable_collision(self, target_widget):
        if target_widget.tangible is not None:
            if target_widget.is_tangible_active:
                if not target_widget.initial_tangible_collision:
                    if target_widget.tangible_effect is not None:
                        for trackable in target_widget.processed_trackables:
                            if trackable.type_id == TrackableTypes.FILE.value:
                                if smath.Math.aabb_in_aabb(target_widget.tangible.aabb, trackable.roi):
                                    if target_widget.tangible.mask.collides_with(trackable.roi):
                                        if target_widget.tangible_effect.effect_type == Effect.EffectType.DELETION.value:
                                            target_widget.on_delete_solo_file.emit(trackable.center)
                                        elif target_widget.tangible_effect.effect_type == Effect.EffectType.MAGNIFICATION.value:
                                            target_widget.on_file_magnification_requested.emit(trackable.id, 0.0)
                                        elif target_widget.tangible_effect.effect_type == Effect.EffectType.TAG.value:
                                            pass

                                        return

    def __handle_brush_assignment(self, trackables, target_widget):
        target_widget.track_hands(trackables, target_widget)

        for trackable in trackables:
            if trackable.type_id == TrackableTypes.HAND.value:
                if trackable.id not in [i.id for i in target_widget.previous_concurrent_hands]:
                    BrushTypeAssignment.action(trackable, target_widget)


class InteractionRegion:

    @staticmethod
    def action(region_overlaps, target_widget, previous_concurrent_hands):
        trackable = region_overlaps[0]

        if len(region_overlaps) > 1:
            region_shapes = region_overlaps[1:]

            if trackable.type_id is not TrackableTypes.HAND.value:
                if trackable.type_id is TrackableTypes.TANGIBLE.value:
                    if target_widget.is_tangible_active:
                        if target_widget.tangible_effect is not None and not target_widget.initial_tangible_collision:

                            # only reasonable effect to apply from tangible to regions is Deletion
                            if target_widget.tangible_effect.effect_type == Effect.EffectType.DELETION.value:

                                to_delete = []

                                for shape in region_shapes:
                                    for i, s in enumerate(target_widget.drawn_shapes):
                                        if shape == s:
                                            to_delete.append(i)

                                for idx in to_delete:
                                    target_widget.on_region_collision_deletion.emit(idx)
                        else:
                            target_widget.tangible_effect = region_overlaps[1].effect
                            target_widget.initial_tangible_collision = True
                else:
                    for shape in region_shapes:
                        if not shape.moveable or (shape.moveable and shape.attached):
                            shape.affect_trackable(trackable)
            else:
                if trackable.colliding_with_shape:
                    if trackable.id not in [i.id for i in previous_concurrent_hands]:
                        target_widget.on_context_menu_open.emit(trackable.position[0],
                                                                trackable.position[1],
                                                                trackable.width,
                                                                trackable.height,
                                                                trackable.id, region_shapes)


class TouchTapEvent:

    @staticmethod
    def action_file(trackable, touch):
        trackable.click(touch.id)

    @staticmethod
    def action_button(trackable, touch):
        trackable.click(touch.id)

    @staticmethod
    def action(touch, target_widget):
        target_widget.on_context_menu_selection.emit(touch.position[0], touch.position[1])

    @staticmethod
    def action_touch(touch, target_widget):
        target_widget.on_touch_tap.emit(touch.position[0], touch.position[1])

    @staticmethod
    def action_region(touch, target_widget, index):
        target_widget.on_palette_selection.emit(index)

    @staticmethod
    def action_region_transfer(touch, target_widget, index):
        target_widget.on_region_effect_transfer_requested.emit(touch.id, index)

    @staticmethod
    def action_file_transfer(trackable, touch, target_widget):
        target_widget.on_file_effect_transfer_requested.emit(touch.id, trackable.id)

class TouchHoldDragEvent:

    @staticmethod
    def action(trackable, touch):
        trackable.drag(touch.center, touch.id)

    @staticmethod
    def action_region(touch, target_widget, shape_idx):
        target_widget.on_region_movement_requested.emit(touch.id, shape_idx)

    @staticmethod
    def action_region_transfer(touch, target_widget, shape_index):
        target_widget.on_region_effect_storage_requested.emit(touch.id, shape_index)


class BrushTypeAssignment:

    @staticmethod
    def action(trackable, target_widget):
        if not trackable.colliding_with_shape:
            target_widget.on_context_menu_open.emit(trackable.position[0],
                                                    trackable.position[1],
                                                    trackable.width,
                                                    trackable.height,
                                                    trackable.id, [])
