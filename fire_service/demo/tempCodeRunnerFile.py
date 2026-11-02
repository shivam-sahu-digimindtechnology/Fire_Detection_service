d=result[0].plot()
    cv2.imshow("fire detection",annotated)
    if cv2.waitKey(1) and 0xFF ==ord('q'):
        break
cap.release()
cv2.destroyWindow()
     