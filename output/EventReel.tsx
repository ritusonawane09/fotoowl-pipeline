import React from 'react';
import {AbsoluteFill, Composition, Img, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';

export const EventReel: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      <Sequence from=0 durationInFrames=120>
        <AbsoluteFill style={{backgroundColor: 'black'}}>
          <Img
            src={staticFile("input_images/DSC_6588.jpg")}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: interpolate(frame - 0, [0, 20], [0, 1], {extrapolateRight: 'clamp'}),
            }}
          />
          {"" && (
            <AbsoluteFill
              style={{
                justifyContent: 'flex-end',
                alignItems: 'center',
                paddingBottom: 90,
                color: 'white',
                fontSize: 44,
                fontFamily: 'sans-serif',
                textShadow: '0 3px 12px rgba(0,0,0,0.65)',
              }}
            >
              <div>{""}</div>
            </AbsoluteFill>
          )}
        </AbsoluteFill>
      </Sequence>
      <Sequence from=120 durationInFrames=120>
        <AbsoluteFill style={{backgroundColor: 'black'}}>
          <Img
            src={staticFile("input_images/DSC_6596.jpg")}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: interpolate(frame - 120, [0, 20], [0, 1], {extrapolateRight: 'clamp'}),
            }}
          />
          {"" && (
            <AbsoluteFill
              style={{
                justifyContent: 'flex-end',
                alignItems: 'center',
                paddingBottom: 90,
                color: 'white',
                fontSize: 44,
                fontFamily: 'sans-serif',
                textShadow: '0 3px 12px rgba(0,0,0,0.65)',
              }}
            >
              <div>{""}</div>
            </AbsoluteFill>
          )}
        </AbsoluteFill>
      </Sequence>
      <Sequence from=240 durationInFrames=120>
        <AbsoluteFill style={{backgroundColor: 'black'}}>
          <Img
            src={staticFile("input_images/DSC_6605.jpg")}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: interpolate(frame - 240, [0, 20], [0, 1], {extrapolateRight: 'clamp'}),
            }}
          />
          {"" && (
            <AbsoluteFill
              style={{
                justifyContent: 'flex-end',
                alignItems: 'center',
                paddingBottom: 90,
                color: 'white',
                fontSize: 44,
                fontFamily: 'sans-serif',
                textShadow: '0 3px 12px rgba(0,0,0,0.65)',
              }}
            >
              <div>{""}</div>
            </AbsoluteFill>
          )}
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="EventReel"
      component={EventReel}
      durationInFrames=360
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
