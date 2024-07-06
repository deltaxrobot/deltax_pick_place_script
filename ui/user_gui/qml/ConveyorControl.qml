import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: rectangle
    implicitHeight: 250
    implicitWidth: 290
    property string device_name: "Conveyor 1"
    signal zeroBtnClicked()
    signal moveSpeedClicked(string speed)
    signal movePositionClicked(string position)
    radius: 3
    border.width: 1

    Text {
        text: device_name
        font.pointSize: 14
        anchors.left: parent.left
        anchors.leftMargin: 5
    }

    Text {
        text: qsTr("Position/Speed:")
        anchors.verticalCenter: conveyorInput.verticalCenter
        font.pointSize: 16
        anchors.left: parent.left
        anchors.leftMargin: 5
    }

    TextField {
        id: conveyorInput
        font.pointSize: 20
        width: 110
        height: 40
        text: "200"
        anchors.top: parent.top
        anchors.topMargin: 40
        anchors.right: parent.right
        anchors.rightMargin: 20
    }

    Button {
        id: setZeroBtn
        objectName: "setZeroBtn"
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 100

        font.pointSize: 25
        display: AbstractButton.TextOnly
        width: 140
        height: 46
        text: "Set Zero"

        background: Rectangle {
            color: "#bfe2a2"
            radius: 10

        }
        onClicked: {
            zeroBtnClicked()
        }
    }

    Button {
        id: movePositionBtn
        objectName: "movePositionBtn"
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.topMargin: 190
        anchors.rightMargin: 5

        font.pointSize: 25
        display: AbstractButton.TextOnly
        width: 130
        height: 50
        text: "Position"

        background: Rectangle {
            color: "#bfe2a2"
            radius: 10

        }
        onClicked: {
            movePositionClicked(conveyorInput.text)
        }
    }

    Button {
        id: moveSpeedBtn
        objectName: "moveSpeedBtn"
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.topMargin: 190
        anchors.leftMargin: 5

        font.pointSize: 25
        display: AbstractButton.TextOnly
        width: 130
        height: 50
        text: "Speed"

        background: Rectangle {
            color: "#bfe2a2"
            radius: 10

        }
        onClicked: {
            moveSpeedClicked(conveyorInput.text)
        }
    }
}
