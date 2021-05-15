import cv2
import time
import numpy as np


class Videotrak:

    @staticmethod
    def get_x_y(trackSettings, img, roibox, imageroi):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if trackSettings.trackingtype == 'Features':
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(2, 2))
            img = clahe.apply(img)
        # remember how big the total image and ROI are
        origheight, origwidth = img.shape[:2]
        roiheight, roiwidth = imageroi.shape[:2]
        # Set up the end of the maximum search time
        searchend = time.time() + 0.2
        finalroidiff = float('inf')
        difflowered = False
        keepgoing = True
        # pull the latest searchx and searchy coordinates from the last known position
        searchx1 = roibox[0][0]
        searchy1 = roibox[0][1]
        if trackSettings.trackingtype == 'Features':
            while keepgoing is True:
                for ycheck in range((searchy1 - 15), (searchy1 + 15)):
                    if time.time() > searchend:
                        break
                    for xcheck in range((searchx1 - 15), (searchx1 + 15)):
                        # check and make sure the new position of the region of interest won't put us over the border of the window, correct back to the edge of border if it would, otherwise take the new roi coordinates
                        if xcheck < 0:
                            xcheck = 0
                        elif xcheck > (origwidth - roiwidth):
                            xcheck = (origwidth - roiwidth)
                        if ycheck < 0:
                            ycheck = 0
                        elif ycheck > (origheight - roiheight):
                            ycheck = (origheight - roiheight)
                        # set up the roi to search within the original image
                        imagecomp = img[ycheck:int(ycheck + roiheight), xcheck:int(xcheck + roiwidth)]
                        # subtract the reference roi from the search area and get the difference of the arrays
                        imagecompforsub = imagecomp.astype(np.int8)
                        imageroiforsub = imageroi.astype(np.int8)
                        imagediff = imagecompforsub - imageroiforsub
                        imagediff = np.absolute(imagediff)
                        imagediff = np.sum(imagediff)
                        imagediff = (imagediff / (np.sum(imageroi))) * 100
                        # if we dropped to a new minimum, save the new minimum diff and save the x and y coordinates we're at.  Set diff lowered flag to true
                        if imagediff < finalroidiff:
                            finalroidiff = imagediff
                            searchx2 = xcheck
                            searchy2 = ycheck
                            difflowered = True
                        # check if we ran out of time
                        if time.time() > searchend:
                            break
                            # back on the keep going loop, check if the diff lowered in the last search run.  If not, we found a local minimum and don't need to keep going.  If we did, start a new search around the new location
                if difflowered is True:
                    keepgoing = True
                    difflowered = False
                else:
                    keepgoing = False
                if time.time() > searchend:
                    print('outtatime')
                    break
                    # print(finalroidiff)
            # figure out if the difference from roi is low enough to be acceptable
            if finalroidiff < 20:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('s'):
                    need_track_feature = True
                searchx1last = searchx2
                searchy1last = searchy2
                learnimg = img[searchy1last:(searchy1last + roiheight), searchx1last:(searchx1last + roiwidth)]
                imageroi = (imageroi * 0.9) + (learnimg * 0.1)
                roibox = [(searchx1last, searchy1last), ((searchx1last + roiwidth), (searchy1last + roiheight))]
                trackSettings.foundtarget = True
            else:
                # print("Didn't find it, keep looking at last known coordinates.")
                searchx1last = roibox[0][0]
                searchy1last = roibox[0][1]
                trackSettings.foundtarget = False
        if trackSettings.trackingtype == 'Bright':
            blurred = cv2.GaussianBlur(img, (5, 5), 0)
            blurred = blurred[searchy1:int(searchy1 + roiheight), searchx1:int(searchx1 + roiwidth)]
            thresh = cv2.threshold(blurred, float(trackSettings.minbright), 255, cv2.THRESH_BINARY)[1]
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
            # cnts = cnts[0]
            cX = []
            cY = []
            # for c in cnts:
            M = cv2.moments(cnts[0])
            try:
                cX.append(int(M["m10"] / M["m00"]))
                cY.append(int(M["m01"] / M["m00"]))
                framestabilized = True
                trackSettings.foundtarget = True
            except:
                print('unable to track this frame')
                trackSettings.foundtarget = False
            if len(cX) > 0:
                cXdiff = (roiwidth / 2) - cX[0]
                cYdiff = (roiheight / 2) - cY[0]
                searchx1 = int(searchx1 - cXdiff)
                searchy1 = int(searchy1 - cYdiff)
                if searchx1 < 0:
                    searchx1 = 0
                if searchy1 < 0:
                    searchy1 = 0
            roibox = [(searchx1, searchy1), ((searchx1 + roiwidth), (searchy1 + roiheight))]
            imageroi = thresh.copy()
        return roibox, imageroi
