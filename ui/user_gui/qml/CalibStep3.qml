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

//                x: model.x - width / 2
//                y: model.y - height / 2

                // onPositionChanged: {

                // }

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
                        canvas.requestPaint();
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
            objectName: "calibImage3"
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

            Canvas {
                id: canvas
                anchors.fill: parent

                onPaint: {
                    var ctx = getContext("2d");
                    ctx.clearRect(0, 0, width, height);

                    ctx.strokeStyle = "red";
                    ctx.lineWidth = 1;

                    // Get the points
//                    var points = [repeater.itemAt(0), repeater.itemAt(1)];
                    var points = [rectangle.list_point[0], rectangle.list_point[1]];

                    // Draw the pentagon
                    ctx.beginPath();
                    ctx.moveTo(points[0].x + points[0].width / 2, points[0].y + points[0].height / 2);
                    ctx.fillStyle = "white";
                    ctx.font = "bold 25px sans-serif";
                    ctx.fillText("P1", points[0].x + points[0].width, points[0].y);
                    for (var i = 1; i < points.length; i++) {
                        ctx.lineTo(points[i].x + points[i].width / 2, points[i].y + points[i].height / 2);
                        ctx.fillText("P2", points[i].x + points[i].width, points[i].y);
                    }
                    ctx.closePath();
                    ctx.stroke();  // Only stroke, do not fill
                }
            }

            Component.onCompleted: {
                var _point_1 = pointDelegate.createObject (calibImage, {
                                              "x" : 300, "y" : 100 , "objectName": "line_p_1"
                                             });
                list_point.push(_point_1)
                var _point_2 = pointDelegate.createObject (calibImage, {
                                              "x" : 600, "y" : 100 , "objectName": "line_p_2"
                                             });
                list_point.push(_point_2)
            }

//            Repeater {
//                id: repeater
//                model: pointsModel
//                delegate: pointDelegate
//            }
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

        Text {
            text: qsTr("Real Distance (mm):")
            anchors.verticalCenter: distance2Point.verticalCenter
            font.pointSize: 14
            anchors.left: parent.left
            anchors.leftMargin: 5
        }

        TextField {
            id: distance2Point
            objectName: "distance2Point"
            font.pointSize: 14
            width: 100
            height: 36
            anchors.left: parent.left
            anchors.leftMargin: 180
            text: "200"
        }

//        Image {
//            source: "file"
//        }

//        Text {

//        }
    }
}
