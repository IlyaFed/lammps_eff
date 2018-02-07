

class visualisation:
    """
    Visualisate calculated results, and make graph, video and etc
    """
    size = (4,6)


    def PT(self, place, size):
        PT = plt.subplot2grid((4, 6), (0, 0), colspan=2, rowspan=2)
    def video(self, filename, start, step, stop, name=""):
        FFMpegWriter = manimation.writers['ffmpeg']
        if name == "":
            name = filename.split("/")[-1]
        metadata = dict(title=name, artist='Lammps visualisator', comment='Visualisation of Lammps eFF data')
        writer = FFMpegWriter(fps=10, metadata=metadata)

        fig = plt.figure(figsize=(20, 10))

PT = plt.subplot2grid((4, 6), (0, 0), colspan=2, rowspan=2)
Tei = plt.subplot2grid((4, 6), (0, 2), colspan=2)
 Pic = plt.subplot2grid((4, 6), (0, 4), colspan=2, rowspan=2)

 P = plt.subplot2grid((4, 6), (2, 0), colspan=2)
 T = plt.subplot2grid((4, 6), (3, 0), colspan=2)
 Mi = plt.subplot2grid((4,6), (2, 4), colspan=2)

 RDF = plt.subplot2grid((4, 6), (1, 2), colspan=2)
 Nei = plt.subplot2grid((4, 6), (2, 2), colspan=2)
 Mr = plt.subplot2grid((4, 6), (3, 4), colspan=2)
 TEXT = plt.subplot2grid((4, 6), (3, 2), colspan=2)

 axes = [PT, Tei, T, P, Mi, Pic, Mr, Nei, RDF, TEXT]

 plt.tight_layout(pad=3)

 first_flag = 1
 color = {"e": "r", "H+": "g", "H": "b", "H2": "c", "H2-": "m", "H2+": "y", "H3": "k", "H3+": "w"}
 with writer.saving(fig, outdirectory + "image/" + visualisation_name + ".mp4", 200):
     for step in range(sstart + sstep, sstop, sstep):
