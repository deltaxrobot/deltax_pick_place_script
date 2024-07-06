import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: rectangle
    color: "#e9e9e9"
    implicitHeight: 514
    implicitWidth: 1362

    Rectangle {
        id: rectangle1
        anchors.left: parent.left
        anchors.right: calibTutorial.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        clip: true



        Text {
            text: qsTr("Robot 1")
            anchors.horizontalCenter: robot1Zarea.horizontalCenter
            font.pointSize: 18
            anchors.top: parent.top
            anchors.topMargin: 4
        }

        Text {
            text: qsTr("Robot 2")
            anchors.horizontalCenter: robot2Zarea.horizontalCenter
            font.pointSize: 18
            anchors.top: parent.top
            anchors.topMargin: 4
        }

        TextField {
            text: qsTr("7")
            anchors.bottom: placing1Area.top
            anchors.bottomMargin: 10
            anchors.horizontalCenter: placing1Area.horizontalCenter
            font.pointSize: 16
            height: 36
            width: 60
            objectName: "minmaxPlace1"
        }

        Grid {
            id: placing1Area
            spacing: 30
            columns: 2
            anchors.left: parent.left
            width: 340
            height: 120
            anchors.top: parent.top
            anchors.topMargin: 90
            anchors.leftMargin: 20

            TextField {
                text: qsTr("-142.4,421.4")
                font.pointSize: 16
                height: 36
                width: 150
                objectName: "placing1P1"
            }

            TextField {
                text: qsTr("-142.4,421.4")
                font.pointSize: 16
                height: 36
                width: 150
                objectName: "placing1P2"
            }

            TextField {
                text: qsTr("-142.4,421.4")
                font.pointSize: 16
                height: 36
                width: 150
                objectName: "placing1P3"
            }

            TextField {
                text: qsTr("-142.4,421.4")
                font.pointSize: 16
                height: 36
                width: 150
                objectName: "placing1P4"
            }
        }

        TextField {
            text: qsTr("2")
            anchors.verticalCenter: placing1Area.verticalCenter
            anchors.left: placing1Area.right
            anchors.leftMargin: 0
            font.pointSize: 16
            height: 36
            width: 50
            objectName: "placing1Row"
        }

        TextField {
            text: qsTr("3")
            anchors.top: placing1Area.bottom
            anchors.topMargin: 0
            anchors.horizontalCenter: placing1Area.horizontalCenter
            font.pointSize: 16
            height: 36
            width: 50
            objectName: "placing1Col"
        }

        TextField {
            text: qsTr("33,14")
            anchors.top: placing1Area.bottom
            anchors.topMargin: 50
            anchors.horizontalCenter: placing1Area.horizontalCenter
            font.pointSize: 16
            height: 36
            width: 150
            objectName: "placing1Offset"
        }

        TextField {
            text: qsTr("1332,1445")
            anchors.top: placing1Area.bottom
            anchors.topMargin: 100
            anchors.horizontalCenter: placing1Area.horizontalCenter
            font.pointSize: 16
            height: 36
            width: 180
            objectName: "pickingZone1"
        }

        TextField {
            text: qsTr("8")
            anchors.bottom: placing2Area.top
            anchors.bottomMargin: 10
            anchors.horizontalCenter: placing2Area.horizontalCenter
            font.pointSize: 16
            height: 36
            width: 60
            objectName: "minmaxPlace2"
        }

        Grid {
            id: placing2Area
            spacing: 30
            columns: 2
            anchors.right: parent.right
            width: 340
            height: 120
            anchors.top: parent.top
            anchors.topMargin: 90
            anchors.rightMargin: 20

            TextField {
                text: qsTr("-142.4,421.4")
                font.pointSize: 16
                height: 36
                width: 150
                objectName: "placing2P1"
            }

            TextField {
                text: qsTr("-142.4,421.4")
                font.pointSize: 16
                height: 36
                width: 150
                objectName: "placing2P2"
            }

            TextField {
                text: qsTr("-142.4,421.4")
                font.pointSize: 16
                height: 36
                width: 150
                objectName: "placing2P3"
            }

            TextField {
                text: qsTr("-142.4,421.4")
                font.pointSize: 16
                height: 36
                width: 150
                objectName: "placing2P4"
            }
        }

        TextField {
            text: qsTr("2")
            anchors.verticalCenter: placing2Area.verticalCenter
            anchors.right: placing2Area.left
            anchors.rightMargin: 5
            font.pointSize: 16
            height: 36
            width: 50
            objectName: "placing2Row"
        }

        TextField {
            text: qsTr("3")
            anchors.top: placing2Area.bottom
            anchors.topMargin: 0
            anchors.horizontalCenter: placing2Area.horizontalCenter
            font.pointSize: 16
            height: 36
            width: 50
            objectName: "placing2Col"
        }

        TextField {
            text: qsTr("33,42")
            anchors.top: placing2Area.bottom
            anchors.topMargin: 50
            anchors.horizontalCenter: placing2Area.horizontalCenter
            font.pointSize: 16
            height: 36
            width: 150
            objectName: "placing2Offset"
        }

        TextField {
            text: qsTr("333,4221")
            anchors.top: placing2Area.bottom
            anchors.topMargin: 100
            anchors.horizontalCenter: placing2Area.horizontalCenter
            font.pointSize: 16
            height: 36
            width: 180
            objectName: "pickingZone2"
        }

        Grid {
            id: robot1Zarea
            anchors.bottom: parent.bottom
            spacing: 15
            anchors.leftMargin: 20
            anchors.bottomMargin: 10
            rows: 0
            columns: 3
            height: 100
            anchors.left: parent.left
            width: 350

            Text {
                text: qsTr("Z Pick")
                font.pointSize: 16

            }

            Text {
                text: qsTr("Z Move")
                font.pointSize: 16

            }

            Text {
                text: qsTr("Z Place")
                font.pointSize: 16

            }

            TextField {
                text: qsTr("-880")
                font.pointSize: 16
                height: 36
                width: 100
                objectName: "robot1ZPick"
            }

            TextField {
                text: qsTr("-830")
                font.pointSize: 16
                height: 36
                width: 100
                objectName: "robot1ZMove"
            }

            TextField {
                text: qsTr("-890")
                font.pointSize: 16
                height: 36
                width: 100
                objectName: "robot1ZPlace"
            }

        }

        Grid {
            id: robot2Zarea
            anchors.bottom: parent.bottom
            spacing: 15
            anchors.rightMargin: 10
            anchors.bottomMargin: 10
            rows: 0
            columns: 3
            height: 100
            anchors.right: parent.right
            width: 350

            Text {
                text: qsTr("Z Pick")
                font.pointSize: 16

            }

            Text {
                text: qsTr("Z Move")
                font.pointSize: 16

            }

            Text {
                text: qsTr("Z Place")
                font.pointSize: 16

            }

            TextField {
                text: qsTr("-880")
                font.pointSize: 16
                height: 36
                width: 100
                objectName: "robot2ZPick"
            }

            TextField {
                text: qsTr("-830")
                font.pointSize: 16
                height: 36
                width: 100
                objectName: "robot2ZMove"
            }

            TextField {
                text: qsTr("-890")
                font.pointSize: 16
                height: 36
                width: 100
                objectName: "robot2ZPlace"
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

        TextField {
            id: newProfileInput
            text: qsTr("")
            anchors.top: parent.top
            anchors.topMargin: 50
            anchors.left: parent.left
            anchors.leftMargin: 20
            font.pointSize: 18
            height: 36
            width: 190
            objectName: "newProfileInput"
        }

        Button {
            font.pointSize: 18
            width: 130
            height: 50
            text: "New"
            anchors.verticalCenter: newProfileInput.verticalCenter
            anchors.left: newProfileInput.right
            anchors.leftMargin: 20

            background: Rectangle {
                color: (!parent.down)?"#bfe2a2":"#b112a2"
                radius: 10

            }

            objectName: "newProfileButton"
        }

        ComboBox {
            id: placeProfiles
            height: 48
            font.pointSize: 18
            width: 190
            model: ["0.5 mm", "1 mm", "5 mm", "10 mm", "50 mm"]
            anchors.left: parent.left
            anchors.leftMargin: 20
            anchors.top: parent.top
            anchors.topMargin: 130

            objectName: "placeProfiles"
        }

        Button {
            font.pointSize: 18
            width: 130
            height: 50
            text: "Load"
            anchors.verticalCenter: placeProfiles.verticalCenter
            anchors.left: placeProfiles.right
            anchors.leftMargin: 20

            background: Rectangle {
                color: (!parent.down)?"#bfe2a2":"#b112a2"
                radius: 10

            }

            objectName: "loadProfile"
        }

        Button {
            font.pointSize: 18
            width: 130
            height: 50
            text: "Delete"

            anchors.left: placeProfiles.right
            anchors.leftMargin: 20
            anchors.top: placeProfiles.bottom
            anchors.topMargin: 50

            background: Rectangle {
                color: (!parent.down)?"#ff7f50":"#b112a2"
                radius: 10

            }

            objectName: "deleteProfile"
        }
    }
}
