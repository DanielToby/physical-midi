import argparse
import mido
from math import pi
from thirdparty.sdf import sdf

# Crank side: contains the threaded spinner and ratchet system.

# Axle side: contains a set screw that rotates against a plastic cap.

class Cylinder:
    def __init__(self, z_height_mm, radius_mm):
        self.z_height_mm = z_height_mm
        self.radius_mm = radius_mm
        self.geometry = self.build_base()

    def build_base(self):
        # Solid cylinder. We will construct the result vertically, with the axle side on the bottom and the crank side on top.
        result = sdf.cylinder(self.radius_mm) & sdf.slab(z0=-0, z1=self.z_height_mm).k(0.1)

        # Both sides expose a lip for the caps to slide onto.
        lip_width_mm = 0.55

        crank_side_lip_depth_mm = 5 
        axle_side_lip_depth_mm = 7.55

        crank_side_lip_negative = sdf.cylinder(self.radius_mm - lip_width_mm) & sdf.slab(z0=self.z_height_mm - crank_side_lip_depth_mm, z1=self.z_height_mm).k(0.1)
        axle_side_lip_negative = sdf.cylinder(self.radius_mm - lip_width_mm) & sdf.slab(z0=0, z1=axle_side_lip_depth_mm).k(0.1)

        result -= crank_side_lip_negative
        result -= axle_side_lip_negative

        return result

    def add_pin(self, z_height_mm, rotation_rad):
        # Pins are constructed with their long side along the X axis.
        # They are then translated to the exterior of the cylinder, up to the desired z height, then rotated around the Z axis.
        # They are twice as long here because half remains in the base.
        pin_length_mm = 0.6
        pin_width_mm = 0.6
        pin_height_mm = 0.6
        pin = sdf.box((pin_length_mm * 2, pin_width_mm, pin_height_mm)).translate((self.radius_mm, 0, z_height_mm)).rotate(rotation_rad, sdf.Z)
        self.geometry = self.geometry | pin

    def save_to_file(self, file_path, step):
        return self.geometry.save(file_path, step)

# This encodes each available midi note.
# Including multiple tines of the same pitch is a feature of music boxes that allows the same note to be played in rapid succession.
# Without this feature, a note struck against a vibrating tine can produce a buzzing sound.
# To support this, we encode duplicates and record accesses to return the "coldest" tine (Z-height).
class Comb:
    def __init__(self, notes, start_height_mm, spacing_mm):
        self.midi_note_to_z_heights = {}
        for i, note in enumerate(notes):

            z_height = start_height_mm + (i * spacing_mm)

            if note in self.midi_note_to_z_heights:
                self.midi_note_to_z_heights[note].append(z_height)
            else:
                self.midi_note_to_z_heights[note] = [z_height]

        self.note_access_counts = { note: 0 for note in self.midi_note_to_z_heights.keys() }

    def get_z_height_mm_for_note(self, note):
        available_z_heights = self.midi_note_to_z_heights[note]
        z_height_mm = available_z_heights[self.note_access_counts[note] % len(available_z_heights)]
        self.note_access_counts[note] += 1 
        return z_height_mm


# This is the only midi data relevant to a music box.
class NoteOnEvent:
    def __init__(self, note, time_stamp):
        self.note = note
        self.time_stamp = time_stamp


# Reads all of the note_on events from a midi file. This is the only relevant data to a music box.
def read_midi_file(midi_file_path):
    note_events = []
    
    current_time_step = 0
    midi_file = mido.MidiFile(midi_file_path)
    for message in midi_file:
        if message.type == 'note_on' and message.velocity > 0:
            current_time_step += message.time
            note_events.append(NoteOnEvent(message.note, current_time_step))

    return note_events

def num_matching(notes, other_notes):
    return len(set(notes) & set(other_notes))

# Transposes through every midi note and returns best match.
def find_best_transposition(input_notes, supported_notes):
    # The range of midi notes is 0 - 127.
    transpose_negative_max = 0 - min(input_notes)
    transpose_positive_max = 127 - max(input_notes)
    
    # Prefer no transposition in the event of a tie.
    best_transposition = 0
    best_score = num_matching(input_notes, supported_notes)

    for transpose_by in range(transpose_negative_max, transpose_positive_max):
        score = num_matching([note + transpose_by for note in input_notes], supported_notes)
        if (score > best_score):
            best_transposition = transpose_by
            best_score = best_score

    return best_transposition

# Searches a four octave range to identify whether or not the note is present in supported_notes.
# Increases the search radius incrementally so that the note is transposed as little as possible.
def find_nearest_octave_or_discard(note, supported_notes, search_depth):
    for i in range(0, search_depth):
        transposed_note = note + (12 * i)
        if transposed_note in supported_notes:
            return transposed_note

        transposed_note = note - (12 * i)
        if transposed_note in supported_notes:
            return transposed_note

    return None

# Adjusts each midi input to the nearest octave within search_depth. Discards notes that can't be encoded.
def clamp_or_discard(input_midi_events, supported_notes, search_depth):
    result = []
    for event in input_midi_events:
        adjusted_note = find_nearest_octave_or_discard(event.note, supported_notes, search_depth)
        if adjusted_note is not None:
            result.append(NoteOnEvent(adjusted_note, event.time_stamp))
    return result

def confirm(message):
    yes = {'yes','y', 'ye', ''}
    no = {'no','n'}

    print(message)
    choice = input().lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        return confirm(message)

# Constructs a music roll using the provided midi data and writes it to output_file_path.
def write_music_box_cylinder_to_file(midi_file_path, output_file_path, no_transpose):
    # The cylinder is constructed from bottom to top, so this order matters.
    comb_midi_notes = [100, 98, 97, 95, 93, 93, 92, 88, 88, 86, 85, 83, 81, 78, 76, 74, 71, 69]

    comb = Comb(comb_midi_notes, start_height_mm=2.0, spacing_mm=0.9)

    cylinder = Cylinder(z_height_mm=20, radius_mm=6.5)

    midi_events = read_midi_file(midi_file_path)
    print(f'Read midi file. Found {len(midi_events)} notes.')

    if not no_transpose:
        # Find the transposition of this data that maximizes the number of notes played.
        best_transposition = find_best_transposition([event.note for event in midi_events], comb_midi_notes)
        midi_events = [NoteOnEvent(event.note + best_transposition, event.time_stamp) for event in midi_events]
        print(f'Transposed by {best_transposition} semitones.')

    # Clean the input data. For each note, clamp it into the desired range. Trim notes that are not represented in the comb.
    cleaned_input_data = clamp_or_discard(midi_events, comb_midi_notes, 0 if no_transpose else 2)

    if len(cleaned_input_data) == 0:
        print('No midi data can be encoded. Exiting.')
        exit()

    # Prompt user to continue if data will be lost.
    if len(cleaned_input_data) < len(midi_events):
        num_discarded = len(midi_events) - len(cleaned_input_data)
        if not confirm(f'Result will exclude {num_discarded} of {len(midi_events)} notes. Continue? [Y/n]'):
            exit()
            
    # Produce a pin on the cylinder for each note in the cleaned input data.
    song_duration = cleaned_input_data[-1].time_stamp
    for event in cleaned_input_data:
        z_height_mm = comb.get_z_height_mm_for_note(event.note)
        # We subtract from 2pi here because of the direction of rotation. (Clockwise when viewed from above)
        rotation_rad = (2 * pi) - (0 if song_duration == 0 else - (event.time_stamp / song_duration) * 2 * pi)
        cylinder.add_pin(z_height_mm, rotation_rad)

    # Write geometry to output file
    cylinder.save_to_file(output_file_path, step = 0.05)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-m', '--midifile',
        metavar='<file>',
        required=True,
        help="The midi file to use as a source."
    )

    parser.add_argument(
        '-f', '--outfile',
        metavar='<file>',
        required=True,
        help="The .stl file to be written."
    )

    parser.add_argument(
        '-n', '--no-transpose',
        action=argparse.BooleanOptionalAction,
        required=False,
        help="Do not transpose the input data to yeild the most encoded notes."
    )

    args = parser.parse_args()
    write_music_box_cylinder_to_file(args.midifile, args.outfile, args.no_transpose if args.no_transpose is True else False)
