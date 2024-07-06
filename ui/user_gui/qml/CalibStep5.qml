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

        Image {
            id: calibImage
            clip: false
            width: 400
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: Image.AlignLeft
            verticalAlignment: Image.AlignTop
            source: "../images/charucox.png"
            anchors.horizontalCenter: parent.horizontalCenter
            scale: 1
            fillMode: Image.PreserveAspectFit

            Button {
                id: setPoint11Btn
                objectName: "setPoint21Btn"
                anchors.top: parent.top
                anchors.right: parent.left
                font.pointSize: 25
                display: AbstractButton.TextOnly
                width: 150
                height: 50
                text: "Point 1"

                background: Rectangle {
                    color: "#bfe2a2"
                    radius: 10

                }
                onClicked: {

                }
            }

            Button {
                id: setPoint12Btn
                objectName: "setPoint22Btn"
                anchors.bottom: parent.bottom
                anchors.left: parent.right
                font.pointSize: 25
                display: AbstractButton.TextOnly
                width: 150
                height: 50
                text: "Point 2"

                background: Rectangle {
                    color: "#bfe2a2"
                    radius: 10

                }
                onClicked: {

                }
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
