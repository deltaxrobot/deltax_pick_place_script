import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: rectangle1

    implicitHeight: 250
    implicitWidth: 380
    property string device_name: "Robot1"
    signal moveRequest(string gcode)
    property string currentStep: "10"

    radius: 3
    border.width: 1

    Text {
        text: device_name
        font.pointSize: 14
    }

    Button {
        id: moveHomeBtn
        objectName:  "moveHomeBtn"
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.topMargin: 5
        anchors.leftMargin: 80

        font.pointSize: 25
        display: AbstractButton.TextOnly
        width: 110
        height: 46
        text: "Home"

        background: Rectangle {
            color: "#bfe2a2"
            radius: 10

        }

        onClicked: {
            moveRequest("G28")
        }
    }

    ComboBox {
        anchors.right: parent.right
        anchors.rightMargin: 10
        height: 48
        anchors.verticalCenter: moveHomeBtn.verticalCenter
        font.pointSize: 18
        width: 140
        model: ["0.5 mm", "1 mm", "5 mm", "10 mm", "50 mm"]

        onActivated: {
            if (currentIndex === 0) {
                currentStep = "0.5"
            }
            else if (currentIndex === 1) {
                currentStep = "1"
            }
            else if (currentIndex === 2) {
                currentStep = "5"
            }
            else if (currentIndex === 3) {
                currentStep = "10"
            }
            else if (currentIndex === 4) {
                currentStep = "50"
            }
        }
    }

    Button {
        id: moveUpBtn
        objectName: "moveUpBtn"
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.topMargin: 70
        anchors.rightMargin: 5

        font.pointSize: 25
        display: AbstractButton.TextOnly
        width: 110
        height: 50
        text: "Up"

        background: Rectangle {
            color: "#bfe2a2"
            radius: 10

        }
        onClicked: {
            var new_gcode = "G01 Z" + currentStep;
            moveRequest(new_gcode)
        }
    }

    Button {
        id: moveDownBtn
        objectName: "moveDownBtn"
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.topMargin: 190
        anchors.rightMargin: 5

        font.pointSize: 25
        display: AbstractButton.TextOnly
        width: 110
        height: 50
        text: "Down"

        background: Rectangle {
            color: "#bfe2a2"
            radius: 10

        }
        onClicked: {
            var new_gcode = "G01 Z-" + currentStep;
            moveRequest(new_gcode)
        }
    }

    Button {
        id: moveLeftBtn
        objectName: "moveLeftBtn"
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.topMargin: 130
        anchors.leftMargin: 5

        font.pointSize: 25
        display: AbstractButton.TextOnly
        width: 100
        height: 50
        text: "Left"

        background: Rectangle {
            color: "#bfe2a2"
            radius: 10

        }
        onClicked: {
            var new_gcode = "G01 X-" + currentStep;
            moveRequest(new_gcode)
        }
    }

    Button {
        id: moveRightBtn
        objectName: "moveRightBtn"
        anchors.left: parent.left
        anchors.leftMargin: 125

        font.pointSize: 25
        display: AbstractButton.TextOnly
        width: 100
        height: 50
        text: "Right"
        anchors.verticalCenter: moveLeftBtn.verticalCenter

        background: Rectangle {
            color: "#bfe2a2"
            radius: 10

        }
        onClicked: {
            var new_gcode = "G01 X" + currentStep;
            moveRequest(new_gcode)
        }
    }

    Button {
        id: moveBackBtn
        objectName: "moveBackBtn"
        anchors.left: parent.left
        anchors.leftMargin: 65
        anchors.top: parent.top
        anchors.topMargin: 70

        font.pointSize: 25
        display: AbstractButton.TextOnly
        width: 100
        height: 50
        text: "Back"

        background: Rectangle {
            color: "#bfe2a2"
            radius: 10

        }
        onClicked: {
            var new_gcode = "G01 Y" + currentStep;
            moveRequest(new_gcode)
        }
    }

    Button {
        id: moveFrontBtn
        objectName: "moveFrontBtn"
        anchors.top: parent.top
        anchors.horizontalCenter: moveBackBtn.horizontalCenter
        anchors.topMargin: 190

        font.pointSize: 25
        display: AbstractButton.TextOnly
        width: 100
        height: 50
        text: "Front"

        background: Rectangle {
            color: "#bfe2a2"
            radius: 10

        }
        onClicked: {
            var new_gcode = "G01 Y-" + currentStep;
            moveRequest(new_gcode)
        }
    }
}
