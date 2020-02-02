
from enum import Enum
from smath import smath
from datastructures.TrackableTypes import TrackableTypes
from datastructures.Trackables import File
import time

import math

from PyQt5 import QtCore, QtGui

import time

class EffectType(Enum):
    MAGNIFICATION = 1
    DELETION = 2
    SEND_EMAIL = 3
    STORAGE = 4
    CONVEYOR_BELT = 5
    DELEGATE = 6
    TAG = 7
    COLLABORATION = 8
    PORTAL = 9
    PALETTE = 10
    COMPOSITE_BASE = 11
    NUM_EFFECTS = 10


class EffectColor(Enum):
    MAGNIFICATION = QtGui.QColor("#644a8c")
    DELETION = QtGui.QColor("#463177")
    SEND_EMAIL = QtGui.QColor("#3bb9d7")
    STORAGE = QtGui.QColor("#00a3d7")
    CONVEYOR_BELT = QtGui.QColor("#84b54e")
    DELEGATE = QtGui.QColor("#66903c")
    TAG = QtGui.QColor("#ebe355")
    COLLABORATION = QtGui.QColor("#ecd121")
    PORTAL = QtGui.QColor("#cf3637")


class Effect:
    def __init__(self, _type):
        self.effect_type = _type


class Magnification(Effect):
    def __init__(self, interval=[], has_gradient=False):
        super().__init__(EffectType.MAGNIFICATION.value)
        self.interval = interval
        self.has_gradient = has_gradient
        self.gradient = []
        self.factor = sum(self.interval) / len(self.interval) / 100
        self.effect_text = '{0}%'.format(self.factor * 100)
        self.effect_color = EffectColor.MAGNIFICATION.value
        self.name = "Magnification"

    def __repr__(self):
        return '\nMagnification:\n' \
               '\tinterval: {0}\n' \
               '\thas gradient: {1}\n' \
               '\tgradient: {2}'.format(self.interval, self.has_gradient, self.gradient)

    def manipulate(self, target, source_shape):
        return self.__magnify(target)

    def __magnify(self, trackable):
        if not self.has_gradient:
            if trackable.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
                trackable.parent.on_pd_magnification_requested.emit(trackable.id, self.factor)
            elif trackable.type_id == TrackableTypes.FILE.value:
                trackable.parent.on_file_magnification_requested.emit(trackable.id, self.factor)
        else:
            # more complicated case
                # use center of trackable for zoom? (e.g. document, file)
            pass

        return None

class RequestCollaboration(Effect):

    def __init__(self, target_user):
        super().__init__(EffectType.COLLABORATION.value)
        self.effect_color = EffectColor.COLLABORATION.value
        self.name = "Collaboration"
        self.target_user = target_user
        self.effect_text = "Collaboration with {}\n".format(target_user)
        self.listeners = []

        self.known_items = {}

    def __repr__(self):
        return '\nRequest Collaboration:\n' \
                '\nTodo'

    def manipulate(self, target, source_shape):
        center_x_target = (target.roi[1][0]+target.roi[2][0])/2
        center_x_source = (source_shape.aabb[1][0]+source_shape.aabb[2][0])/2
        if(abs(center_x_target - center_x_source) < 2):
            if target.id not in self.known_items.keys() or (time.time() - self.known_items[target.id]) > 1:
                target.parent.on_halt_file_for_review.emit(target.id)
                self.known_items[target.id] = time.time()
            else:
                target.parent.on_file_halted_for_review.emit(target.id)
        return None

class Portal(Effect):
    def __init__(self):
        super().__init__(EffectType.PORTAL)
        self.effect_text = 'Portal'
        self.effect_color = EffectColor.PORTAL.value
        self.name = "Portal"

    def __repr__(self):
        return "Portal Region Effect"

    def manipulate(self, target, source_shape):
        return None


class Deletion(Effect):
    def __init__(self):
        super().__init__(EffectType.DELETION.value)

        self.effect_text = ''
        self.effect_color = EffectColor.DELETION.value
        self.name = "Deletion"

    def __repr__(self):
        return 'Deletion'

    def manipulate(self, target, source_shape):
        return self.__delete(target)

    def __delete(self, target):
        if target.type_id == TrackableTypes.FILE.value:
            if not target.grabbed:
                target.parent.on_delete_solo_file.emit(target.center)
        elif target.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
            target.parent.on_delete_digital_twin.emit(target.id)

        return None


class SendMail(Effect):
    def __init__(self, receiver):
        super().__init__(EffectType.SEND_EMAIL.value)

        self.receiver = receiver

        self.effect_text = 'To ' + self.receiver
        self.effect_color = EffectColor.SEND_EMAIL.value
        self.source_shape = None
        self.name = "Send Mail"

    def __repr__(self):
        return 'Send via Email\n' \
               '\tReceiver: {0}'.format(self.receiver)

    def manipulate(self, target, source_shape):
        return self.__send_via_email(target, source_shape)

    def __send_via_email(self, target, source_shape):
        self.source_shape = source_shape

        if target.type_id == TrackableTypes.FILE.value or target.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
            if not target.emailed:
                target.emailed = True
                source_shape.parent.on_thread_visualization_requested.emit(source_shape.roi, target.id)

        return None


class Storage(Effect):
    def __init__(self):
        super().__init__(EffectType.STORAGE.value)
        self.effect_text = ''
        self.effect_color = EffectColor.STORAGE.value
        self.name = "Storage"

    def __repr__(self):
        return 'Storage'

    def manipulate(self, target, source_shape):
        return self.__store(target, source_shape)

    def __store(self, target, source_shape):
        if target.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
            if not target.stored:
                target.stored = True

                x, y = target.center[0], target.center[1]
                target.parent.on_new_file_append_requested.emit(x, y, 'CHI\'19.txt' if target.id == 1 else 'PD_Logo.png', target.id)
        elif target.type_id == TrackableTypes.FILE.value:
            if not target.stored:
                target.stored = True

                target.parent.on_thread_visualization_requested.emit(source_shape.roi, target.id)

        return None


class ConveyorBelt(Effect):
    def __init__(self, items=[], looped=False, is_composite=False, n_composite_regions=4):
        super().__init__(EffectType.CONVEYOR_BELT.value)

        self.items = items
        self.looped = looped
        self.traveled_to_line = []
        self.target_points = []
        self.effect_text = ''
        self.effect_color = None
        self.name = "Conveyor Belt"
        self.is_composite = is_composite
        self.n_composite_regions = n_composite_regions

    def __repr__(self):
        return 'Conveyor_Belot\n' \
               '\tLooped: {0}\n' \
               '\tNumber of Items: {1}\n' \
               '\tItems:\n' \
               '\t\t{2}'.format(self.looped, len(self.items), self.items)

    def manipulate(self, target, source_shape):
        if target.type_id == TrackableTypes.FILE.value:
            if not target.is_on_conveyor_belt:
                line = source_shape.middle_line

                min_distance = float(math.inf)
                idx = 0

                for i in range(len(line)):
                    d = smath.Math.vector_norm((target.center[0] - line[i][0], target.center[1] - line[i][1]))

                    if d < min_distance:
                        min_distance = d
                        idx = i

                units_per_second = 12000
                travel_length = sum([smath.Math.vector_norm([i[0], i[1]]) for i in line[idx:]])

                actual_animation_time = travel_length / units_per_second * 1000
                target.parent.on_conveyor_move_requested.emit(target.center[0], target.center[1], idx, line, actual_animation_time, self.looped, self.is_composite, self.n_composite_regions)

        return None




class CompositeBase(Effect):
    def __init__(self,):
        super().__init__(EffectType.COMPOSITE_BASE.value)

        self.name = "Composite Base"
        self.effect_text = "Composite Base"
        self.effect_color = EffectColor.DELEGATE.value
        self.regions = 3
        self.source_shape = None
        self.my_conveyor_belt = None
        self.known_items = []

    def __repr__(self):
        return 'Composite'

    # this is a copy-pasted and slightly modified version of the conveyor-belt manipulate
    def manipulate(self, target, source_shape):
        self.source_shape = source_shape
        if target.type_id == TrackableTypes.FILE.value:
            if not target.is_on_conveyor_belt:
                line = self.my_conveyor_belt.middle_line

                min_distance = float(math.inf)
                idx = 0

                for i in range(len(line)):
                    d = smath.Math.vector_norm((target.center[0] - line[i][0], target.center[1] - line[i][1]))

                    if d < min_distance:
                        min_distance = d
                        idx = i

                units_per_second = 12000
                travel_length = sum([smath.Math.vector_norm([i[0], i[1]]) for i in line[idx:]])

                actual_animation_time = travel_length / units_per_second * 1000
                target.parent.on_conveyor_move_requested.emit(target.center[0], target.center[1], idx, line, actual_animation_time, False, True, self.regions)
                self.known_items.append(id(target))




class Delegate(Effect):
    def __init__(self, receiver):
        super().__init__(EffectType.DELEGATE.value)

        self.receiver = receiver
        self.effect_text = 'To ' + self.receiver
        self.effect_color = EffectColor.DELEGATE.value
        self.name = "Delegate"
        self.source_shape = None

    def __repr__(self):
        return 'Delegate\n' \
               '\tReceiver: {0}'.format(self.receiver)

    def manipulate(self, target, source_shape):
        self.source_shape = source_shape

        if target.type_id == TrackableTypes.FILE.value or target.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
            if not target.delegated:
                target.delegated = True
                source_shape.parent.on_thread_visualization_requested.emit(source_shape.roi, target.id)


class Tag(Effect):
    def __init__(self, tagging):
        super().__init__(EffectType.TAG.value)

        self.effect_color = EffectColor.TAG.value
        self.name = "Tag"
        self.tagging = tagging
        self.effect_text = "Tag with " + self.tagging

    def __repr__(self):
        return "Tag"

    def manipulate(self, target, source_shape):
        if target.type_id == TrackableTypes.FILE.value:
            if not target.done_at_once:
                target.done_at_once = True
                source_shape.parent.on_do_at_once_requested.emit(source_shape.roi, target.id, self.tagging)


class Palette(Effect):
    def __init__(self):
        super().__init__(EffectType.PALETTE.value)

        """
            MAGNIFICATION = QtGui.QColor("#644a8c")
    DELETION = QtGui.QColor("#463177")
    SEND_EMAIL = QtGui.QColor("#3bb9d7")
    STORAGE = QtGui.QColor("#00a3d7")
    CONVEYOR_BELT = QtGui.QColor("84b54e")
    DELEGATE = QtGui.QColor("#66903c")
    TAG = QtGui.QColor("#ebe355")
    COLLABORATION = QtGui.QColor("#ecd121")
    PORTAL = QtGui.QColor("#cf3637")
        """


        self.name = 'Palette'
        self.effect_colors = [
            EffectColor.MAGNIFICATION.value,
            EffectColor.DELETION.value,
            EffectColor.SEND_EMAIL.value,
            EffectColor.STORAGE.value,
            EffectColor.CONVEYOR_BELT.value,
            EffectColor.DELEGATE.value,
            EffectColor.TAG.value,
            EffectColor.COLLABORATION.value,
            EffectColor.PORTAL.value
        ]

        self.effect_text = ""
        self.effect_color = None

    def __repr__(self):
        return 'Palette'

    def manipulate(self, target, source_shape):
        if target.type_id == TrackableTypes.TOUCH.value:
            print("palette clicked")
