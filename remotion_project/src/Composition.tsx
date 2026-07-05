import React from "react";
import { AbsoluteFill, Img, Sequence, staticFile } from "remotion";

export const MyComposition: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Sequence from={0} durationInFrames={120}>
        <Img
          src={staticFile("input_images/DSC_6588.jpg")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      </Sequence>

      <Sequence from={120} durationInFrames={120}>
        <Img
          src={staticFile("input_images/DSC_6596.jpg")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      </Sequence>

      <Sequence from={240} durationInFrames={120}>
        <Img
          src={staticFile("input_images/DSC_6605.jpg")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      </Sequence>
    </AbsoluteFill>
  );
};