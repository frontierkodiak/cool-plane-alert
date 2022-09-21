import larynx


class vocalization_string:
    def __init__(self, filtered_plane_info_df):
        self.filtered_plane_info_df = filtered_plane_info_df
        self.vocalization_string = self.get_vocalization_string()

    def get_vocalization_string(self):
        manufacturer = self.filtered_plane_info_df['manufacturername']
        model = self.filtered_plane_info_df['model']
        distance = self.filtered_plane_info_df['distance']
        vocalization_string = "There is a " + manufacturer + " " + model + " " + distance + " miles away."
        return vocalization_string
