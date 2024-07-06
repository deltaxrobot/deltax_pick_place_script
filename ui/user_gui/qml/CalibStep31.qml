import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: rectangle
    color: "#e9e9e9"
    implicitHeight: 514
    implicitWidth: 1362

    property var list_point: []

    Rectangle {
        anchors.left: parent.left
        anchors.right: calibTutorial.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        clip: true

        PinchArea {
            anchors.fill: parent
            pinch.target: calibImage
            pinch.minimumScale: 0.1
            pinch.maximumScale: 10
            pinch.dragAxis: Pinch.XAndYAxis

            MouseArea {
                id: selectd1ragArea;
                drag.target: calibImage
                drag.axis: Drag.XAndYAxis
                scrollGestureEnabled: true;
                acceptedButtons: Qt.RightButton;
                anchors.fill: parent
                hoverEnabled: false

                onPressed: selectd1ragArea.cursorShape = Qt.ClosedHandCursor
                onReleased: selectd1ragArea.cursorShape = Qt.ArrowCursor
            }
        }

        Component {
            id: pointDelegate

            Rectangle {
                id: rect
                width: 30
                height: 30
                color: "transparent"
                border.width: 1

                signal mouseReleased()

//                x: model.x - width / 2
//                y: model.y - height / 2

                // onPositionChanged: {

                // }

                Rectangle {
                    width: 2
                    height: 2
                    color: "#fc0303"
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter

                }

                MouseArea {
                    id: mouseArea
                    anchors.fill: parent
                    drag.target: parent

                    property int begin_x: 0
                    property int begin_y: 0

                    onPressed: {
                        begin_x = mouseArea.mouseX
                        begin_y = mouseArea.mouseY
                    }

                    onPositionChanged: {
                        rect.x += (mouseArea.mouseX - begin_x);
                        rect.y += (mouseArea.mouseY - begin_y);
                    }

                    onReleased: {
                        rect.mouseReleased()
                    }
                }
            }
        }

        ListModel {
            id: pointsModel

            ListElement { x: 300; y: 100 }
            ListElement { x: 600; y: 100 }
        }

        Image {
            id: calibImage
            objectName: "calibImage4"
            cache: false
            x: 0
            y: 0
            z: 0
            clip: false
            //width: parent.width
            //height: parent.height
            horizontalAlignment: Image.AlignLeft
            verticalAlignment: Image.AlignTop
            source: "../images/deltaxmodel.png"
            scale: 1
//            fillMode: Image.PreserveAspectFit
            fillMode: Image.Pad

            Component.onCompleted: {
                var _point_1 = pointDelegate.createObject (calibImage, {
                                              "x" : 200, "y" : 200 , "objectName": "real_point"
                                             });
            }
        }
    }

    Rectangle {
        id: calibTutorial
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 500
        color: "#e9e9e9"

        anchors.topMargin: 70
        anchors.bottomMargin: 70

//        Image {
//            source: "file"
//        }

//        Text {

//        }
    }
}
